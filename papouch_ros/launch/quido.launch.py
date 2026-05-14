from launch import LaunchContext, LaunchDescription
from launch.actions import OpaqueFunction
from launch.launch_description_entity import LaunchDescriptionEntity

from papouch_ros.launch_helpers import quido_node, quido_args, SetupContext


def launch_setup(
        context: LaunchContext, *args, **kwargs
) -> list[LaunchDescriptionEntity]:
    ctx = SetupContext(context)

    return [quido_node(usb=ctx.config("usb"), eth=ctx.config("eth"))]


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        quido_args() +
        [OpaqueFunction(function=launch_setup)]
    )
