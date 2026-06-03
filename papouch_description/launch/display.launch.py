from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
from papouch_ros.launch_helpers_common import parameter_value_xacro

def generate_launch_description():
    description_package = FindPackageShare("papouch_description")
    default_model_path = PathJoinSubstitution(
        [description_package, "urdf", "papouch.xacro"]
    )
    default_rviz_config_path = PathJoinSubstitution(
        [description_package, "rviz", "papouch.rviz"]
    )

    model = LaunchConfiguration("model")
    rviz_config = LaunchConfiguration("rviz_config")

    robot_description = {
        "robot_description": parameter_value_xacro(model, {})
    }

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "model",
                default_value=default_model_path,
                description="Absolute path to the gripper URDF file.",
            ),
            DeclareLaunchArgument(
                "rviz_config",
                default_value=default_rviz_config_path,
                description="Absolute path to the RViz configuration file.",
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[robot_description],
            ),
            Node(
                package="joint_state_publisher_gui",
                executable="joint_state_publisher_gui",
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                arguments=["-d", rviz_config],
                output="screen",
            ),
        ]
    )
