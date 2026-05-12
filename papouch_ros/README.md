# ROS package for Papouch Devices

This package provides ROS related stuff for the communication with the Papouch devices, namely the Quido family of IO modules. 


## Installation

Dependencies:

 - [papouch](https://github.com/rop-ctu/papouch/)


## ROS1

In order to enable the ROS support clone this repository and the `papouch` inside the ROS workspace i.e:

``` shell
cs [ros/ssh] # your ros workspace


git clone https://github.com/rop-ctu/papouch.git
git clone https://github.com/rop-ctu/papouch_ros.git
cd papouch
sudo python setup.py install
cd ..

cd papouch_ros
catkin build
source devel/setup.sh
```

Then do the `catkin build` as normal in order to register the package. The ros node is then started with:

``` shell
rosrun papouch_ros quido_node --dev /dev/ttyACM0
```

Note that the quido device may appear under different name than `/dev/ttyACM0`. If you are using ETH version of the quido use the following command instead:

``` shell
rosrun papouch_ros quido_node --eth 192.168.1.2
```

Providing appropriate IP address of the device. The node then provides the following services:

- `~write_io` with the service description [papouch_ros/WriteIO](papouch_ros/srv/WriteIO.srv). Use to write outputs of the quido module. Multiple outputs can be written using single request.
