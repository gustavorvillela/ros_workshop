cmake_minimum_required(VERSION 3.8)
project(robo_lp)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

add_executable(route_mapper src/route_mapper.cpp)
ament_target_dependencies(route_mapper rclcpp nav_msgs sensor_msgs geometry_msgs)

install(TARGETS route_mapper DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY urdf worlds config launch DESTINATION share/${PROJECT_NAME})

ament_package()
