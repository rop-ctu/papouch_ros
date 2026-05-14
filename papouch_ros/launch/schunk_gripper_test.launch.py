from launch import LaunchContext, LaunchDescription
from launch.actions import OpaqueFunction
from launch.launch_description_entity import LaunchDescriptionEntity
from launch_ros.actions import Node
from papouch_ros.launch_helpers import (
    quido_node,
    quido_args,
    schunk_gripper_node,
    schunk_gripper_args,
    SetupContext,
)


def launch_setup(
        context: LaunchContext, *args, **kwargs
) -> list[LaunchDescriptionEntity]:
    ctx = SetupContext(context)

    quido_node_name = 'quido'
    schunk_node_name = 'schunk_server'
    ns = 'test'

    schunk_test_node = Node(
        package="papouch_ros",
        executable="schunk_gripper_test",
        output="screen",
        namespace=ns,
    )

    return [
        quido_node(usb=ctx.config("usb"),
                   eth=ctx.config("eth"),
                   name=quido_node_name,
                   ),
        schunk_gripper_node(namespace=ns),
        #schunk_gripper_node(ctx.config_path("schunk_gripper_params")),
        schunk_test_node,
    ]


def generate_launch_description():
    return LaunchDescription(
        quido_args() +
        schunk_gripper_args() +
        [OpaqueFunction(function=launch_setup)]
    )
