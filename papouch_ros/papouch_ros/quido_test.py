import argparse
from rclpy.node import Node
import rclpy
import time
from papouch_ros_idl.srv import WriteIO
from . import node_utils as utils

DEFAULT_NODE_NAME = "quido_client"
OUT_CHANNELS = [0, 1, 2, 3, 4]


class QuidoTestClientNode(Node):

    def __init__(self, server: str = "quido"):
        super().__init__(DEFAULT_NODE_NAME)

        self.client = utils.service_client(self, WriteIO, server + '/io')

    def send_request(self, channel, state):
        request = WriteIO.Request()
        request.channel = channel
        request.state = state

        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        return future.result().retval

    def do_work(self):
        for channel in OUT_CHANNELS:
            for state in [True, False]:
                self.get_logger().info(f"Sending {channel}: {state}")
                response = self.send_request([channel], [state])
                self.get_logger().info(f"Response: {response}")
                time.sleep(1)


def main(args=None):
    parser = argparse.ArgumentParser(__name__)
    parser.add_argument("--server", type=str, default='quido')

    utils.init_spin_node(args, QuidoTestClientNode, parser)


if __name__ == "__main__":
    main()
