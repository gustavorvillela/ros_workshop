# Aula 6 — aula6.launch.py
# Sobe a simulação, o color_masks (Aula 4), o cylinder_detector (Aula 5) e o
# cylinder_follower (Aula 6), que leva o robô até o cilindro da cor escolhida.
# Com rqt:=true, abre a imagem anotada e o rqt_plot com o erro e a saída dos dois PIDs.
# Uso: ros2 launch robo_py aula6.launch.py cor:=azul            (rqt:=false para não abrir janelas)
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
    cor = LaunchConfiguration('cor')
    sim_time = {'use_sim_time': True}

    sim = IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(
        get_package_share_directory('robo_gazebo'), 'launch', 'sim.launch.py')))

    masks = Node(package='robo_py', executable='color_masks', parameters=[sim_time],
                 output='screen')
    detector = Node(package='robo_py', executable='cylinder_detector', parameters=[sim_time],
                    output='screen')
    follower = Node(package='robo_py', executable='cylinder_follower',
                    parameters=[sim_time, {'cor': cor}], output='screen')

    imagem = Node(package='rqt_image_view', executable='rqt_image_view',
                  arguments=['/vision/annotated'], condition=IfCondition(rqt))
    # data = [erro, P, I, D, saída]: o gráfico mostra o erro e a saída de cada PID
    grafico = Node(package='rqt_plot', executable='rqt_plot',
                   arguments=['/pid/angular/data[0]', '/pid/angular/data[4]',
                              '/pid/linear/data[0]', '/pid/linear/data[4]'],
                   condition=IfCondition(rqt))

    return LaunchDescription([
        DeclareLaunchArgument('cor', default_value='verde',
                              description='Cor do cilindro: vermelho, verde, azul ou amarelo'),
        DeclareLaunchArgument('rqt', default_value='true',
                              description='Abre a imagem anotada e o gráfico dos PIDs'),
        sim, masks, detector, follower, imagem, grafico,
    ])
