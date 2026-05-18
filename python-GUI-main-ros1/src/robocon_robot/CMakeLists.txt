cmake_minimum_required(VERSION 3.0.2)
project(robocon_robot)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
)

catkin_python_setup()
catkin_package()

catkin_install_python(PROGRAMS
  scripts/robot_command_subscriber
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
