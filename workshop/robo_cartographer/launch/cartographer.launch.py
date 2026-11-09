# Aula 3 — cartographer.launch.py (pronto)
# Reaproveita o launch do turtlebot3_cartographer, só trocando a configuração
# pelo config/robo_2d.lua deste pacote.
# Uso: ros2 launch robo_cartographer cartographer.launch.py
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    config_dir = os.path.join(get_package_share_directory('robo_cartographer'), 'config')
    tb3_launch = os.path.join(
        get_package_share_directory('turtlebot3_cartographer'), 'launch', 'cartographer.launch.py')

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(tb3_launch),
            launch_arguments={
                'use_sim_time': 'True',
                'cartographer_config_dir': config_dir,
                'configuration_basename': 'robo_2d.lua',
            }.items()),
    ])
