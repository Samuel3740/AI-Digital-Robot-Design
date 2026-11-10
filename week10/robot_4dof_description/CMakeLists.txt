cmake_minimum_required(VERSION 3.8)
project(robot_4dof_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf config launch
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS scripts/point_to_point.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
