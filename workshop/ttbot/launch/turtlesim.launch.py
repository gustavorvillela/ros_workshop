"""Plano B: sobe o turtlesim e o desviador da tartaruga.

Uso:
  ros2 launch ttbot turtlesim.launch.py
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='turtlesim', executable='turtlesim_node', name='turtlesim'),

        Node(
            package='ttbot',
            executable='desviador_turtlesim',
            name='desviador',
            output='screen',
            parameters=[{
                'distancia': 1.0,
                'velocidade': 1.5,
                'velocidade_giro': 1.5,
            }],
        ),
    ])
