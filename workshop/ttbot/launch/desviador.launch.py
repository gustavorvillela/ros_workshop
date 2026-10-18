"""Sobe o TurtleBot3 no Gazebo (turtlebot3_world) e o nó desviador.

Uso:
  ros2 launch ttbot desviador.launch.py                        # roda o exercício
  ros2 launch ttbot desviador.launch.py no:=desviador_solucao  # roda a versão pronta
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Os launch files do TurtleBot3 leem o modelo do robô desta variável de ambiente
    os.environ.setdefault('TURTLEBOT3_MODEL', 'burger')

    mundo = os.path.join(
        get_package_share_directory('turtlebot3_gazebo'), 'launch', 'turtlebot3_world.launch.py')

    return LaunchDescription([
        DeclareLaunchArgument(
            'no', default_value='desviador',
            description='Executável do pacote ttbot: desviador ou desviador_solucao'),

        IncludeLaunchDescription(PythonLaunchDescriptionSource(mundo)),

        Node(
            package='ttbot',
            executable=LaunchConfiguration('no'),
            name='desviador',
            output='screen',
            parameters=[{
                'use_sim_time': True,  # usa o relógio do Gazebo
                'distancia': 0.5,
                'velocidade': 0.15,
                'velocidade_giro': 0.8,
            }],
        ),
    ])
