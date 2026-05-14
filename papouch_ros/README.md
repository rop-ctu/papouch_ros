# ROS2 package for Papouch Devices

This package provides ROS2 related stuff for the communication with the Papouch devices, namely the Quido family of IO modules. 


## Installation

Clone this repository inside the ROS2 workspace. Note a dependency (`papouch` package) cloned as a git submodule. Than run standard `colcon build` command.

``` shell
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

git clone --recursive https://github.com/rop-ctu/papouch_ros.git
cd ..

# Install all dependencies that are available as binaries
source "/opt/ros/$ROS_DISTRO/setup.bash"
sudo apt-get update
rosdep update --rosdistro "$ROS_DISTRO"
rosdep install -y -i --from-paths src --rosdistro $ROS_DISTRO

# Build workspace
colcon build
source ~/ros2_ws/install/setup.bash
```

## Running

Nodes providing service can be run directly.

``` shell
ros2 run papouch_ros quido_node --usb /dev/ttyACM0
ros2 run papouch_ros quido_node --eth 192.168.100.23
```

Or a launch files can be used (or imported into a complex launch system). 

``` shell
ros2 launch papouch_ros quido.launch.py usb:=/dev/ttyACM0
ros2 launch papouch_ros quido.launch.py eth:=192.168.100.31
```

