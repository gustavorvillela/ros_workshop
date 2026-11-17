# Aula 7 — aula7.launch.py
# Junta tudo: a sala nova (sala2.sdf) no Gazebo, o Cartographer fazendo o mapa, a visão
# (color_masks e cylinder_detector), o cylinder_follower com os PIDs e a missao, que leva o
# robô de cilindro em cilindro. Complete os TODO 1 a 3.
# Uso: ros2 launch robo_py aula7.launch.py            (rqt:=false para não abrir a imagem)
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

    # TODO 1: incluir o sim.launch.py do robo_gazebo (como no aula6.launch.py), passando
    #   launch_arguments={'mundo': 'sala2.sdf'}.items() para abrir a sala nova.
    sim = None

    # TODO 2: incluir o cartographer.launch.py do robo_cartographer (Aula 3), que já abre
    #   o RViz com o mapa.
    slam = None

    masks = Node(package='robo_py', executable='color_masks', parameters=[sim_time],
                 output='screen')
    detector = Node(package='robo_py', executable='cylinder_detector', parameters=[sim_time],
                    output='screen')
    # Ganhos da Aula 6: troque pelos que vocês escolheram na sintonia. O follower começa
    # parado (sem cor e sem giro de busca): quem diz para onde ir é a missao.
    follower = Node(package='robo_py', executable='cylinder_follower',
                    parameters=[sim_time, {'cor': 'nenhuma', 'w_busca': 0.0,
                                           'kp_ang': 1.0, 'kp_lin': 0.3}],
                    output='screen')
    imagem = Node(package='rqt_image_view', executable='rqt_image_view',
                  arguments=['/vision/annotated'], condition=IfCondition(rqt))

    # TODO 3: um Node do executável 'missao' deste pacote, com use_sim_time e o parâmetro
    #   'sequencia': a lista de cores na ordem que vocês planejaram, por exemplo
    #   {'sequencia': ['verde', 'azul', 'amarelo', 'vermelho']}.
    missao = None

    acoes = [sim, slam, masks, detector, follower, imagem, missao]
    return LaunchDescription([
        DeclareLaunchArgument('rqt', default_value='true',
                              description='Abre o rqt_image_view em /vision/annotated'),
    ] + [a for a in acoes if a is not None])
