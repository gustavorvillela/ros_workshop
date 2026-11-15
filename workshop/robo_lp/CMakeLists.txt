cmake_minimum_required(VERSION 3.8)
project(robo_lp)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(message_filters REQUIRED)
find_package(vision_msgs REQUIRED)
find_package(OpenCV REQUIRED COMPONENTS core imgproc)

add_executable(route_mapper src/route_mapper.cpp)
ament_target_dependencies(route_mapper rclcpp nav_msgs sensor_msgs geometry_msgs)

# Aula 4
add_executable(color_masks src/color_masks.cpp)
ament_target_dependencies(color_masks rclcpp sensor_msgs cv_bridge)
target_link_libraries(color_masks ${OpenCV_LIBS})

# Aula 5
add_executable(cylinder_detector src/cylinder_detector.cpp)
ament_target_dependencies(cylinder_detector rclcpp sensor_msgs cv_bridge message_filters vision_msgs)
target_link_libraries(cylinder_detector ${OpenCV_LIBS})

install(TARGETS route_mapper color_masks cylinder_detector DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})

ament_package()
