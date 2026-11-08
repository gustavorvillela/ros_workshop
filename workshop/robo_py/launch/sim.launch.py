# Aula 2 — sim.launch.py
# Abre o mundo sala.sdf, publica o robot_description a partir do xacro,
# cria o robô no Gazebo e liga a ponte Gazebo <-> ROS 2. Complete os TODO 1 e 2.
# Uso: ros2 launch robo_py sim.launch.py
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = get_package_share_directory('robo_py')
    world = os.path.join(pkg, 'worlds', 'sala.sdf')
    xacro_file = os.path.join(pkg, 'urdf', 'robo.urdf.xacro')
    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    gz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': f'-r {world}'}.items())
    rsp = Node(package='robot_state_publisher', executable='robot_state_publisher',
               parameters=[{'robot_description': robot_description, 'use_sim_time': True}])

    # TODO 1: nó 'create' do pacote ros_gz_sim, que cria o robô no Gazebo.
    #   - deve ler o URDF publicado no tópico robot_description
    #   - nome do modelo: robo; altura inicial: 0.45 m
    #   Dica: ros2 run ros_gz_sim create --help
    spawn = None

    # TODO 2: nó 'parameter_bridge' do pacote ros_gz_bridge.
    #   - parâmetro config_file apontando para config/bridge.yaml deste pacote
    #   - use_sim_time ligado, como no rsp acima
    bridge = None

    return LaunchDescription([gz, rsp, spawn, bridge])
