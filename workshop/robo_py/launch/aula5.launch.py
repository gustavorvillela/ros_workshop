# Aula 5 — aula5.launch.py
# Sobe tudo de uma vez: a simulação (robo_gazebo), o route_mapper da Aula 3 levando o
# robô pelos waypoints, o color_masks da Aula 4 e o cylinder_detector da Aula 5, e abre
# o rqt_image_view na imagem anotada. Complete os TODO 1 a 3.
# Uso: ros2 launch robo_py aula5.launch.py            (rqt:=false para não abrir a janela)
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    rqt = LaunchConfiguration('rqt')
    sim_time = {'use_sim_time': True}

    sim = IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(
        get_package_share_directory('robo_gazebo'), 'launch', 'sim.launch.py')))

    # Aula 3: leva o robô pelos waypoints padrão (o quadrado em volta da caixa central)
    route = Node(package='robo_py', executable='route_mapper', parameters=[sim_time],
                 output='screen')

    # TODO 1: um Node do pacote 'robo_py', executável 'color_masks', com parameters=[sim_time]
    #   e output='screen', guardado em masks.

    # TODO 2: o mesmo para 'cylinder_detector', em detector, com os parâmetros
    #   [sim_time, {'min_area': 200.0}].

    # TODO 3: um Node do pacote 'rqt_image_view', executável 'rqt_image_view', com
    #   arguments=['/vision/annotated'] e condition=IfCondition(rqt), para só abrir a janela
    #   quando rqt for 'true'. Guarde em viewer.

    # Depois, acrescente masks, detector e viewer na lista abaixo.
    return LaunchDescription([
        DeclareLaunchArgument('rqt', default_value='true',
                              description='Abre o rqt_image_view em /vision/annotated'),
        sim, route,
    ])
