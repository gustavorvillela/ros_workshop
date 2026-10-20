"""Sobe o TurtleBot3 no Gazebo (turtlebot3_world), o RViz e o nó desviador.

Uso:
  ros2 launch ttbot desviador.launch.py                        # roda o exercício
  ros2 launch ttbot desviador.launch.py no:=desviador_solucao  # roda a versão pronta
  ros2 launch ttbot desviador.launch.py rviz:=false            # sem o RViz, só o Gazebo
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Os launch files do TurtleBot3 leem o modelo do robô desta variável de ambiente
    os.environ.setdefault('TURTLEBOT3_MODEL', 'burger')

    tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    mundo = os.path.join(tb3_gazebo, 'launch', 'turtlebot3_world.launch.py')
    # Config do próprio TurtleBot3: modelo do robô, laser, odometria e TF, a partir do frame odom
    config_rviz = os.path.join(tb3_gazebo, 'rviz', 'tb3_gazebo.rviz')

    return LaunchDescription([
        DeclareLaunchArgument(
            'no', default_value='desviador',
            description='Executável do pacote ttbot: desviador ou desviador_solucao'),

        DeclareLaunchArgument(
            'rviz', default_value='true',
            description='Abre o RViz junto com o Gazebo: true ou false'),

        IncludeLaunchDescription(PythonLaunchDescriptionSource(mundo)),

        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', config_rviz],
            # Sem o relógio do Gazebo, o RViz acha o laser velho demais e não desenha os pontos
            parameters=[{'use_sim_time': True}],
            condition=IfCondition(LaunchConfiguration('rviz')),
        ),

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
