from launch import LaunchContext, LaunchDescription
from launch.actions import OpaqueFunction
from launch.launch_description_entity import LaunchDescriptionEntity
from launch_ros.actions import Node
from papouch_ros.launch_helpers import quido_node, quido_args, SetupContext


def launch_setup(
        context: LaunchContext, *args, **kwargs
) -> list[LaunchDescriptionEntity]:
    ctx = SetupContext(context)

    quido_node_name = 'quido_server'
    ns = 'test'

    quido_test_node = Node(
        package="papouch_ros",
        executable="quido_test",
        output="screen",
        arguments=['--server', quido_node_name],
        namespace=ns,
    )

    return [
        quido_node(usb=ctx.config("usb"),
                   eth=ctx.config("eth"),
                   name=quido_node_name,
                   namespace=ns,
                   ),
        quido_test_node
    ]


def generate_launch_description():
    return LaunchDescription(
        quido_args() +
        [OpaqueFunction(function=launch_setup)]
    )
