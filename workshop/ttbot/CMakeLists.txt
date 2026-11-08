cmake_minimum_required(VERSION 3.8)
project(ttbot)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

add_executable(obstacle_avoider src/obstacle_avoider.cpp)
ament_target_dependencies(obstacle_avoider rclcpp sensor_msgs geometry_msgs)

install(TARGETS obstacle_avoider DESTINATION lib/${PROJECT_NAME})

ament_package()
