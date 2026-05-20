from typing import Optional
import argparse
from rclpy.node import Node
import sys
from papouch import Quido, QuidoError
from papouch_ros_idl.srv import WriteIO
from . import node_utils as utils

DEFAULT_NODE_NAME = "quido"


class QuidoNode(Node):

    def __init__(self,
                 usb: Optional[str] = None,
                 eth: Optional[str] = None,
                 ):
        super().__init__(DEFAULT_NODE_NAME)

        # initialize quido class
        self.quido = Quido()
        if usb is not None:
            if eth is not None:
                self.get_logger().error(
                    "Only one of --usb or --eth must be given")
                sys.exit(1)

            self.get_logger().info(f"Connecting to Quido USB on {usb}")
            self.quido.connect_usb(usb)

        elif eth is not None:
            self.get_logger().info(f"Connecting to Quido ETH on {eth}")
            self.quido.connect_tcp(eth)
        else:
            self.get_logger().info(
                "Neither --usb nor --eth is given, running in dummy mode")
            self.quido = None

        self.srv = utils.service_server(self, WriteIO, 'io', self.write_io_cb)

    def write_io_cb(self, req: WriteIO.Request, response: WriteIO.Response
                    ) -> WriteIO.Response:
        response.retval = True

        if self.quido is None:  # dummy mode, only log-print info
            for i, s in zip(req.channel, req.state):
                self.get_logger().info(f"DUMMY QUIDO {i} -> {s}")
            self.get_logger().info(f"DUMMY QUIDO ---")
            return response

        try:
            for i, s in zip(req.channel, req.state):
                self.quido.set_output(i, s)

        except QuidoError as e:
            self.get_logger().error(e.__str__())
            response.retval = False

        return response


def main(args=None):
    parser = argparse.ArgumentParser(__name__)
    parser.add_argument("--usb", type=str, required=False)
    parser.add_argument("--eth", type=str, required=False)

    utils.init_spin_node(args, QuidoNode, parser)


if __name__ == "__main__":
    main()
