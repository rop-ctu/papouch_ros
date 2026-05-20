import argparse
from typing import Optional, Callable
import rclpy
from rclpy.node import Node
from rclpy.parameter import parameter_value_to_python
from rclpy.action import ActionClient, ActionServer
from rclpy.client import Client

import os
from rclpy.node import SrvTypeRequest, SrvTypeResponse, Service

ros_distro = os.environ.get("ROS_DISTRO")
if ros_distro == 'humble':
    from rcl_interfaces.srv import GetParameters


    class AsyncParameterClient:
        def __init__(self, self_node, remote_node_name):
            self.client = self_node.create_client(GetParameters,
                                                  remote_node_name + '/get_parameters')

        def wait_for_services(self, *args, **kwargs):
            return self.client.wait_for_service(*args, **kwargs)

        def get_parameters(self, param_list):
            req = GetParameters.Request()
            req.names = param_list
            future = self.client.call_async(req)
            return future
else:
    from rclpy.parameter_client import AsyncParameterClient


def init_spin_node(args, node_class: type,
                   arg_parser: Optional[argparse.ArgumentParser] = None):
    node = None
    try:
        rclpy.init(args=args)

        if arg_parser is not None:
            args = rclpy.utilities.remove_ros_args(args)
            args = arg_parser.parse_args(args[1:])  # skip the script name
            node = node_class(**vars(args))
        else:
            node = node_class()

        if hasattr(node, "do_work"):
            while rclpy.ok():
                rclpy.spin_once(node, timeout_sec=0.0)
                node.do_work()

        else:
            rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok:
            rclpy.shutdown()


def node_namespace(self_node: Node) -> str:
    """Node namespace always ending with a slash."""

    ns = self_node.get_namespace()
    assert ns.startswith('/')
    return ns if ns == '/' else ns + '/'


def get_param_list_from_node(self_node: Node, remote_node_name: str,
                             param_list: list[str]) -> list:
    """Returns parameters from a (different) running node by its name."""

    param_client = AsyncParameterClient(self_node, remote_node_name)

    while not param_client.wait_for_services(timeout_sec=1.0):
        self_node.get_logger().warning(
            f"Parameters of {remote_node_name} not available, waiting..."
        )

    future = param_client.get_parameters(param_list)

    rclpy.spin_until_future_complete(self_node, future)

    result = future.result()
    if result is not None:
        return [parameter_value_to_python(x) for x in result.values]

    raise RuntimeError(f'Failed to get parameters of {remote_node_name}')


def get_params_from_node(self_node: Node, remote_node_name: str, cls: type):
    """Returns parameters from a (different) running node by its name."""

    params = cls()
    param_list = [k for k in dir(params) if not k.endswith('_')]
    print(param_list, flush=True)

    values = get_param_list_from_node(self_node, remote_node_name, param_list)

    for (k, v) in zip(param_list, values):
        setattr(params, k, v)

    return params


def action_client(self_node: Node,
                  action_type: type,
                  action_name: str) -> ActionClient:
    """Create an action client and connects it to a server."""

    client = ActionClient(self_node, action_type, action_name)

    # add namespace of to action server name if not absolute (for printing)
    if not action_name.startswith('/'):
        # name is relative to the node namespace
        action_name = node_namespace(self_node) + action_name

    while not client.wait_for_server(timeout_sec=1.0):
        self_node.get_logger().warn(
            f'Waiting for action server {action_name}...')

    self_node.get_logger().info(f'Connected to action: {action_name}')

    return client


def action_server(self_node: Node, action_type: type,
                  action_name: str,
                  callback: Callable,
                  **kwargs) -> ActionServer:
    """Create an action server."""

    if not action_name.startswith('/'):
        # name is relative to the node name (with namespace)
        action_name = node_namespace(self_node) + self_node.get_name() + \
                      '/' + action_name

    action = ActionServer(
        self_node, action_type, action_name, callback, **kwargs)

    self_node.get_logger().info(f"Action server started: {action_name}")

    return action


def service_client(self_node: Node, srv_type: type,
                   srv_name: str, **kwargs) -> Client:
    """Create a service client and connects it to a server."""

    if not srv_name.startswith('/'):
        # name is relative to the node namespace
        srv_name = node_namespace(self_node) + srv_name

    client = self_node.create_client(srv_type, srv_name, **kwargs)

    while not client.wait_for_service(timeout_sec=1.0):
        self_node.get_logger().warn(
            f'Waiting for service {srv_name}...')

    self_node.get_logger().info(
        f'Connected to service: {client.srv_name}')

    return client


def service_server(
        self_node: Node, srv_type: type,
        srv_name: str,
        callback: Callable[[SrvTypeRequest, SrvTypeResponse], SrvTypeResponse],
        **kwargs
) -> Service:
    """Create a service."""

    if not srv_name.startswith('/'):
        # name is relative to the node name (with namespace)
        srv_name = node_namespace(self_node) + self_node.get_name() + \
                   '/' + srv_name

    srv = self_node.create_service(srv_type, srv_name, callback)
    self_node.get_logger().info(f"Service started: {srv.srv_name}")
    return srv
