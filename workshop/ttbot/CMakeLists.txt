cmake_minimum_required(VERSION 3.8)
project(ttbot)

# Gera build/ttbot/compile_commands.json, usado pelo autocomplete do VS Code
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(turtlesim REQUIRED)

# Aula 1 (turtlesim): exercício com TODOs e versão pronta
add_executable(desviador_turtlesim src/desviador_turtlesim.cpp)
ament_target_dependencies(desviador_turtlesim rclcpp geometry_msgs turtlesim)

add_executable(desviador_turtlesim_solucao src/desviador_turtlesim_solucao.cpp)
ament_target_dependencies(desviador_turtlesim_solucao rclcpp geometry_msgs turtlesim)

# Aula 2 (TurtleBot3 no Gazebo): exercício com TODOs e versão pronta
add_executable(desviador src/desviador.cpp)
ament_target_dependencies(desviador rclcpp geometry_msgs sensor_msgs)

add_executable(desviador_solucao src/desviador_solucao.cpp)
ament_target_dependencies(desviador_solucao rclcpp geometry_msgs sensor_msgs)

install(TARGETS
  desviador_turtlesim desviador_turtlesim_solucao
  desviador desviador_solucao
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME})

ament_package()
