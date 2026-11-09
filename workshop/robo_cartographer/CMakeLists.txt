cmake_minimum_required(VERSION 3.8)
project(robo_cartographer)

find_package(ament_cmake REQUIRED)

# O robo_2d.lua que você cria na Aula 3 é instalado daqui
install(DIRECTORY config launch DESTINATION share/${PROJECT_NAME})

ament_package()
