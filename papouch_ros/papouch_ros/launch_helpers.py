from typing import Optional

from launch import Substitution
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from .launch_helpers_common import *  # noqa: F401, F403


def quido_node(usb: Optional[str] = None,
               eth: Optional[str] = None,
               **kwargs
               ) -> Node:
    return Node(
        package="papouch_ros",
        executable="quido_node",
        arguments=
        (["--usb", usb] if usb not in (None, "") else []) +
        (["--eth", eth] if eth not in (None, "") else []),
        output="screen",
        **kwargs
    )


def quido_args():
    return [
        DeclareLaunchArgument(
            "usb",
            default_value="",
            description="USB device to connect.",
        ),

        DeclareLaunchArgument(
            "eth",
            default_value="",
            description="IP address to connect.",
        ),
    ]


def schunk_gripper_node(
        schunk_gripper_params: Optional[str|Substitution] = None,
        **kwargs
) -> Node:
    return Node(
        package="papouch_ros",
        executable="schunk_gripper_node",
        parameters=(
            [schunk_gripper_params] if schunk_gripper_params is not None else []),
        output="screen",
        **kwargs
    )


def schunk_gripper_args():
    return [
        DeclareLaunchArgument(
            "schunk_gripper_params",
            default_value="config/schunk_gripper_parameters.yaml",
            description="Gripper parameters (yaml file).",
        ),
    ]
