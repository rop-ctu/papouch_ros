#!/bin/bash
export RCUTILS_COLORIZED_OUTPUT=1
source ~/ros2_ws/install/setup.bash

# Connection can be given as e.g. ETH=192.168.100.31

OPTS=()
if [ -n "$ETH" ]; then 
    OPTS=("eth:=$ETH")
fi

ros2 launch papouch_ros quido_test.launch.py ${OPTS[@]}
