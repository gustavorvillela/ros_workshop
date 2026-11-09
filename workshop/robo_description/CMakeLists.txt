cmake_minimum_required(VERSION 3.8)
project(robo_description)

find_package(ament_cmake REQUIRED)

# O robo.urdf.xacro que você cria na Aula 2 é instalado daqui
install(DIRECTORY urdf DESTINATION share/${PROJECT_NAME})

ament_package()
