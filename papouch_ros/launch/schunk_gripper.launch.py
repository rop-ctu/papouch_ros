from launch import LaunchContext, LaunchDescription
from launch.actions import OpaqueFunction
from launch.launch_description_entity import LaunchDescriptionEntity

from papouch_ros.launch_helpers import (
    schunk_gripper_node,
    schunk_gripper_args,
    SetupContext,
)


def launch_setup(
        context: LaunchContext, *args, **kwargs
) -> list[LaunchDescriptionEntity]:
    ctx = SetupContext(context)

    return [schunk_gripper_node(ctx.config_path("schunk_gripper_params"))]


def generate_launch_description():
    return LaunchDescription(
        schunk_gripper_args() +
        [OpaqueFunction(function=launch_setup)]
    )
