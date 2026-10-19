import math
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch.event_handlers import OnProcessExit

def generate_launch_description():
    pkg_name = 'ttbot' 
    exec_name = 'move_ttbot'

    # Declarar os argumentos aceitos pelo launch file
    side_length_arg = DeclareLaunchArgument(
        'side_length',
        default_value='2.5',
        description='Tamanho do lado do quadrado em metros (m)'
    )

    # Obter os valores configurados/passados na linha de comando
    side_length = LaunchConfiguration('side_length')

    # Cálculo dinâmico do tempo em linha reta: tempo = distancia / velocidade
    linear_time = PythonExpression([side_length, ' / ', '1'])

    # Criamos os 8 nós da sequência (4 lados + 4 curvas)
    nodes = []
    for i in range(4):
        # 1. Avançar (fw)
        nodes.append(Node(
            package=pkg_name,
            executable=exec_name,
            name=f'square_fw_{i+1}',
            arguments=['1', 'fw', linear_time],
            output='screen'
        ))
        # 2. Girar 90° para a esquerda (ccw)
        nodes.append(Node(
            package=pkg_name,
            executable=exec_name,
            name=f'square_ccw_{i+1}',
            arguments=['0.25', 'ccw', '6.2831'],
            output='screen'
        ))

    # Encadeia a execução: quando o nó N encerra (exit), inicia o nó N+1
    event_handlers = []
    for i in range(len(nodes) - 1):
        event_handlers.append(
            RegisterEventHandler(
                OnProcessExit(
                    target_action=nodes[i],
                    on_exit=[nodes[i+1]]
                )
            )
        )

    return LaunchDescription([
        side_length_arg,
        nodes[0],
        *event_handlers
    ])