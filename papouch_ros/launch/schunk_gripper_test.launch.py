from launch import LaunchContext, LaunchDescription
from launch.actions import OpaqueFunction
from launch.launch_description_entity import LaunchDescriptionEntity
from launch_ros.actions import Node
from papouch_ros.launch_helpers import (
    quido_node,
    quido_args,
    schunk_gripper_node,
    schunk_gripper_args,
    required_node,
    SetupContext,
)

PKG = 'papouch_ros'


def launch_setup(
        context: LaunchContext, *args, **kwargs
) -> list[LaunchDescriptionEntity]:
    ctx = SetupContext(context, pkg=PKG)

    quido_node_name = 'quido'
    ns = 'test'

    schunk_test_node = Node(
        package="papouch_ros",
        executable="schunk_gripper_test",
        output="screen",
        namespace=ns,
    )

    return [
        *required_node(quido_node(usb=ctx.config("usb"),
                                  eth=ctx.config("eth"),
                                  name=quido_node_name,
                                  namespace=ns,
                                  )),
        schunk_gripper_node(ctx.config_path("schunk_gripper_params"),
                            namespace=ns),
        schunk_test_node,
    ]


def generate_launch_description():
    return LaunchDescription(
        quido_args() +
        schunk_gripper_args() +
        [OpaqueFunction(function=launch_setup)]
    )
