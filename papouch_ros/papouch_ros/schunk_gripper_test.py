from rclpy.node import Node
import rclpy
import time
import argparse
from . import node_utils as utils
from control_msgs.action import GripperCommand
from std_srvs.srv import SetBool
from papouch_ros.schunk_gripper_parameters import schunk_gripper_params

DEFAULT_NODE_NAME = "schunk_gripper_client"


class SchunkGripperTestClientNode(Node):

    def __init__(self, server: str = "schunk_gripper"):
        super().__init__(DEFAULT_NODE_NAME)

        self.params: schunk_gripper_params.Params = \
            utils.get_params_from_node(self, server,
                                       schunk_gripper_params.Params)

        self.rate = self.create_rate(1.0)
        self.opened = False

        self.client = utils.action_client(self, GripperCommand,
                                          server + '/' +
                                          self.params.action_name)

        self.srv_client = utils.service_client(self, SetBool,
                                               server + '/' +
                                               self.params.service_name_simple)

    def open_close_by_action(self):
        self.opened = not self.opened

        action_goal = GripperCommand.Goal()
        action_goal.command.position = (self.params.joint_max_pos
                                        if self.opened else
                                        self.params.joint_min_pos)

        # send goal
        self.client.wait_for_server()

        self.get_logger().info(
            f"Sending goal {action_goal.command.position}")

        goal_future = self.client.send_goal_async(action_goal)
        rclpy.spin_until_future_complete(self, goal_future)
        goal_handle = goal_future.result()

        if not goal_handle.accepted:
            self.get_logger().warn('Goal rejected')
            return

        self.get_logger().info('Goal accepted')

        # wait for the result
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        result = result_future.result().result
        self.get_logger().info(f'Result: {result}')

    def open_close_by_service(self):
        self.opened = not self.opened

        request = SetBool.Request()
        request.data = not self.opened

        self.get_logger().info(f"Sending request {request.data}")
        future = self.srv_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        self.get_logger().info(f"Got response {future.result()}")

    def do_work(self):
        self.open_close_by_action()
        time.sleep(1)
        self.open_close_by_action()
        time.sleep(1)

        self.open_close_by_service()
        time.sleep(1)
        self.open_close_by_service()
        time.sleep(1)


def main(args=None):
    parser = argparse.ArgumentParser(__name__)
    parser.add_argument("--server", type=str, default='schunk_gripper')

    utils.init_spin_node(args, SchunkGripperTestClientNode)


if __name__ == "__main__":
    main()
