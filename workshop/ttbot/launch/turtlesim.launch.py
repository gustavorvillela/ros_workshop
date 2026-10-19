"""Sobe o turtlesim e o desviador da tartaruga.

Uso:
  ros2 launch ttbot turtlesim.launch.py                                  # roda o exercício
  ros2 launch ttbot turtlesim.launch.py no:=desviador_turtlesim_solucao  # roda a versão pronta
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'no', default_value='desviador_turtlesim',
            description='Executável do pacote ttbot: desviador_turtlesim ou desviador_turtlesim_solucao'),

        Node(package='turtlesim', executable='turtlesim_node', name='turtlesim'),

        Node(
            package='ttbot',
            executable=LaunchConfiguration('no'),
            name='desviador',
            output='screen',
            parameters=[{
                'distancia': 1.0,
                'velocidade': 1.5,
                'velocidade_giro': 1.5,
            }],
        ),
    ])
