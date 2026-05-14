import argparse
from rclpy.node import Node
import time
from papouch_ros_idl.srv import WriteIO
from control_msgs.action import GripperCommand

from rclpy.callback_groups import ReentrantCallbackGroup

from sensor_msgs.msg import JointState
from std_srvs.srv import SetBool
from rclpy.qos import QoSProfile, ReliabilityPolicy
from rclpy.action import ActionServer
from . import node_utils as utils
from papouch_ros.schunk_gripper_parameters import schunk_gripper_params

DEFAULT_NODE_NAME = "schunk_gripper"


class SchunkGripperException(Exception):

    def __init__(self, msg=''):
        self.msg = msg

    def __str__(self):
        return "SchunkGripperException: " + self.msg


class SchunkGripperNode(Node):
    """Class for Quido based Schunk gripper"""

    def __init__(self, dummy_mode: bool = False):
        super().__init__(DEFAULT_NODE_NAME)

        # parameters, state
        self.param_listener = schunk_gripper_params.ParamListener(self)
        self.params = self.param_listener.get_params()
        self.dummy_mode = dummy_mode
        self.stay_energized = self.params.stay_energized
        self.joint_state = 0.0
        self.last_cmd_stamp = self.get_clock().now().nanoseconds / 1e9

        # message prototype
        self.joint_state_msg = JointState()
        self.joint_state_msg.header.frame_id = ''
        self.joint_state_msg.name = [self.params.joint_name]
        self.joint_state_msg.position = [self.joint_state]

        # The service client callback must run in a different callback group
        # that the future in the WriteIO client waiting for WriteIO server
        # to complete. Otherwise, a deadlock occurs.
        self.io_client_cb_group = ReentrantCallbackGroup()

        # action server for the gripper comman
        self.action_server = ActionServer(
            self,
            GripperCommand,
            self.get_name() + '/' + self.params.action_name,
            self.action_execute_cb)

        # service for the simple gripper open/close
        self.srv = self.create_service(
            SetBool,
            self.get_name() + '/' + self.params.service_name_simple,
            self.gripper_activate_cb)

        # service to change the stay energized flag
        self.stay_energized_srv = self.create_service(
            SetBool,
            self.get_name() + '/' + self.params.service_name_stay_energized,
            self.set_stay_energized_cb)

        # publish joint states publisher and loop
        self.joint_state_pub = self.create_publisher(
            JointState,
            "joint_states",
            qos_profile=QoSProfile(depth=50,
                                   reliability=ReliabilityPolicy.RELIABLE),
        )

        self.state_timer = self.create_timer(self.params.joint_state_dt,
                                             self.publish_state)

        # write IO service client
        self.client = utils.service_client(self, WriteIO,
                                           self.params.write_io_srv,
                                           callback_group=self.io_client_cb_group)

        # start with unenergized gripper
        coro = self.write_io(False, False)
        # TODO probably hack to make immediate blocking call of coroutine
        coro.send(None)

    async def set_stay_energized_cb(self, req: SetBool.Request,
                                    res: SetBool.Response) -> SetBool.Response:
        """Callback function for set_stay_energized service."""

        # copy flag from request
        self.stay_energized = req.data

        # un-energize the gripper if stay_energized is false
        if not self.stay_energized:
            await self.write_io(False, False)

        # return response
        res.success = True
        return res

    async def gripper_activate_cb(self, req: SetBool.Request,
                                  res: SetBool.Response) -> SetBool.Response:
        """Callback function for the simple open/close."""

        do_close = req.data

        self.get_logger().info(f"Received new request: {do_close}")

        result = await self.gripper_activate(do_close)

        self.get_logger().info(f"Result: {result}")

        res.success = result
        return res

    async def action_execute_cb(self, goal_handle):
        """Callback function for gripper command action."""

        action_goal: GripperCommand.Goal = goal_handle.request
        goal_position = action_goal.command.position

        self.get_logger().info(f"Received new position goal: {goal_position}")

        do_close = abs(self.params.joint_min_pos - goal_position) < abs(
            self.params.joint_max_pos - goal_position)

        result = await self.gripper_activate(do_close)

        goal_handle.succeed()

        return GripperCommand.Result(position=self.joint_state)

    async def gripper_activate(self, do_close: bool) -> bool:
        """Activate the gripper - open or close using IO."""

        result = True
        try:
            # un-energize the gipper
            await self.write_io(False, False)

            # convert linear position to discreate state
            if do_close:
                self.get_logger().info(f"Closing")
                goal_position = self.params.joint_min_pos
                await self.write_io(False, True)
            else:
                self.get_logger().info(f"Opening")
                goal_position = self.params.joint_max_pos
                await self.write_io(True, False)

            # wait for gripper to finish its movement
            time.sleep(self.params.time_of_motion)  # TODO respect ROS time

            # un-energize the gripper if stay_energized is fasle
            if not self.stay_energized:
                await self.write_io(False, False)

            # set joint state
            self.joint_state = goal_position

        except SchunkGripperException as e:
            self.get_logger().error(str(e))
            result = False

        return result

    async def write_io(self, open_sig_state: bool, close_sig_state: bool):
        self.get_logger().debug(
            f'write_io(open_sig_state={open_sig_state}, close_sig_state={close_sig_state})')

        # sleep between commands if this command is too soon
        t_now = self.get_clock().now().nanoseconds / 1e9

        t_rest = self.params.time_between_commands - (
                t_now - self.last_cmd_stamp)
        if t_rest > 0.0:
            time.sleep(t_rest)  # TODO use ROS time

        # call service if not in dummy mode
        if not self.dummy_mode:
            req = WriteIO.Request()
            req.channel = [self.params.open_io, self.params.close_io]
            req.state = [int(open_sig_state), int(close_sig_state)]

            future = self.client.call_async(req)
            response = await future

            # check output
            if response is None or not response.retval:
                raise SchunkGripperException("Failed to set quido outputs!")

        # store the stamp of this command
        self.last_cmd_stamp = self.get_clock().now().nanoseconds / 1e9

    def publish_state(self):
        # update time stamp
        self.joint_state_msg.header.stamp = self.get_clock().now().to_msg()

        # update position
        self.joint_state_msg.position = [self.joint_state]

        # publish message
        self.joint_state_pub.publish(self.joint_state_msg)


def main(args=None):
    parser = argparse.ArgumentParser(__name__)
    parser.add_argument("--dummy-mode", action="store_true")
    utils.init_spin_node(args, SchunkGripperNode, parser)


if __name__ == "__main__":
    main()
