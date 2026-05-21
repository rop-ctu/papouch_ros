#!/bin/bash

source "/opt/ros/$ROS_DISTRO/setup.bash"
cd ~/ros2_ws || exit 255

sudo apt-get update || exit 255

rosdep update --rosdistro "$ROS_DISTRO" || exit 255

rosdep install -y -i --from-paths src --rosdistro $ROS_DISTRO || exit 255
