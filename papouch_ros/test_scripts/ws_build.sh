#!/bin/bash
# Build workspace

cd ~/ros2_ws || exit 255

source "/opt/ros/$ROS_DISTRO/setup.bash"

export MAKEFLAGS="-j 4"

colcon build \
       --symlink-install \
       --merge-install \
       --cmake-args \
       --no-warn-unused-cli \
       -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
       -DCMAKE_BUILD_TYPE=Release \
       -DBUILD_TESTING=OFF \
       -DBUILD_BENCHMARK=OFF \
       -DBUILD_BENCHMARKS=OFF \
       -DBUILD_EXAMPLES=OFF \
       -DINSTALL_DOCUMENTATION=OFF \
       -DBUILD_PYTHON_INTERFACE=ON \
       -DGENERATE_PYTHON_STUBS=OFF \
       -DBUILD_WITH_MULTITHREADS=ON \
       "$@"
