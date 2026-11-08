"""Aula 3 — route_mapper.

Faz o robô percorrer uma lista de pontos (waypoints) usando a odometria, para o
Cartographer mapear a sala sozinho. Complete os TODO 1 a 8 (o 9 é extensão).
Rode com: ros2 run robo_py route_mapper --ros-args -p use_sim_time:=true
"""
import math

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist


class RouteMapper(Node):

    def __init__(self):
        super().__init__('route_mapper')

        # TODO 1: declarar os parâmetros com self.declare_parameter(nome, padrão).value:
        #   waypoints (lista de floats, pares x, y no frame odom; padrão: quadrado de 6 m
        #   [6.0, 0.0, 6.0, 6.0, 0.0, 6.0, 0.0, 0.0]), v_max = 0.3, w_max = 0.5,
        #   tolerance = 0.10, k_lin = 0.5, k_ang = 1.5
        self.v_max = self.w_max = self.tol = self.k_lin = self.k_ang = 0.0

        # TODO 2: converter os waypoints em self.route, uma lista de tuplas (x, y)
        self.route = []

        self.idx = 0              # índice do ponto atual
        self.x = self.y = self.yaw = 0.0
        self.have_odom = False
        self.done = False

        # TODO 3: assinar '/odom' (Odometry) chamando self.on_odom

        # TODO 4: criar o publisher de '/cmd_vel' (Twist) em self.cmd_pub
        self.cmd_pub = None

        # TODO 5: criar um timer de 0.1 s que chama self.step

    def on_odom(self, msg):
        # TODO 3 (continuação): guardar self.x, self.y e self.yaw e marcar self.have_odom = True.
        #   yaw a partir do quaternion q = msg.pose.pose.orientation:
        #   math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
        pass

    def step(self):
        cmd = Twist()  # começa zerado = robô parado

        # TODO 6: sem odometria ainda, ou com o percurso terminado (self.idx >= len(self.route)),
        #   publicar cmd parado e sair (return). Avisar no log uma única vez (use self.done):
        #   self.get_logger().info('Percurso concluído: salve o mapa agora')

        # TODO 7: calcular a distância até self.route[self.idx] (math.hypot) e o erro de rumo
        #   (ângulo até o ponto menos self.yaw), normalizado com math.atan2(math.sin(e), math.cos(e)).

        # TODO 8: escolher a ação:
        #   - dist < self.tol: avisar no log e passar ao próximo ponto (self.idx += 1)
        #   - abs(erro) > 0.2 rad: girar no lugar, w = self.k_ang * erro
        #   - senão: andar, v = self.k_lin * dist, corrigindo o rumo com w = self.k_ang * erro
        #   Limite v a self.v_max e w a [-self.w_max, self.w_max] com min e max.

        if self.cmd_pub is not None:
            self.cmd_pub.publish(cmd)

    # TODO 9 (extensão): assinar '/scan' e não andar se algo estiver a menos de 0,3 m.


def main(args=None):
    rclpy.init(args=args)
    node = RouteMapper()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
