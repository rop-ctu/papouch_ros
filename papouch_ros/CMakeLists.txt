cmake_minimum_required(VERSION 3.22)
project(papouch_ros)

# Dependencies
find_package(ament_cmake_auto REQUIRED)
ament_auto_find_build_dependencies()

generate_parameter_module(
  schunk_gripper_parameters
  papouch_ros/schunk_gripper_parameters.yaml
)

ament_python_install_package(${PROJECT_NAME} SCRIPTS_DESTINATION
                             lib/${PROJECT_NAME})
ament_python_install_package(papouch PACKAGE_DIR ../papouch/papouch/)
ament_auto_package(INSTALL_TO_SHARE config launch)
