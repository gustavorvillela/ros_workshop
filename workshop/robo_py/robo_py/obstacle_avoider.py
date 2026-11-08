"""Aula 1 — obstacle_avoider.

Lê o lidar (/scan) e publica velocidades (/cmd_vel): anda para frente e
gira no lugar quando há um obstáculo dentro de um cone à frente do robô.
Complete os TODO 1 a 4.
Rode com: ros2 run robo_py obstacle_avoider --ros-args -p use_sim_time:=true
"""
import math

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist, TwistStamped


class ObstacleAvoider(Node):

    def __init__(self):
        super().__init__('obstacle_avoider')
        # Parâmetros (podem ser mudados sem editar o código: -p nome:=valor)
        self.max_speed = self.declare_parameter('max_speed', 0.15).value        # m/s (o Burger vai até ~0.22)
        self.turn_speed = self.declare_parameter('turn_speed', 0.8).value       # rad/s
        self.safe_distance = self.declare_parameter('safe_distance', 0.5).value  # m
        self.cone_deg = self.declare_parameter('cone_deg', 30.0).value          # meia-abertura do cone, em graus
        # Confira o tipo esperado com: ros2 topic info -v /cmd_vel
        self.use_stamped = self.declare_parameter('use_stamped', True).value    # TwistStamped (True) ou Twist (False)

        # TODO 1: criar o publisher de 'cmd_vel' em self.pub, com fila de 10 mensagens.
        #   O tipo é TwistStamped se self.use_stamped for True, senão Twist.
        self.pub = None

        # TODO 2: assinar 'scan' (LaserScan) com QoS de sensor (qos_profile_sensor_data),
        #   chamando self.on_scan a cada mensagem. Guarde em self.sub.

    def on_scan(self, scan):
        half_cone = math.radians(self.cone_deg)
        min_dist = math.inf

        # TODO 3: percorrer scan.ranges e guardar em min_dist a menor leitura válida
        #   dentro do cone frontal (abs(ângulo) <= half_cone).
        #   - ângulo do raio i: scan.angle_min + i * scan.angle_increment
        #   - o lidar do TurtleBot3 vai de 0 a 2*pi: normalize com math.atan2(math.sin(a), math.cos(a))
        #   - leitura válida: math.isfinite(r) e scan.range_min <= r <= scan.range_max
        #   Dica: for i, r in enumerate(scan.ranges):

        cmd = Twist()
        # TODO 4: se min_dist < self.safe_distance, girar no lugar (cmd.angular.z);
        #   senão, andar para frente (cmd.linear.x).

        self.publish(cmd)

    def publish(self, cmd):
        """Pronto: publica cmd no tipo certo para o robô."""
        if self.pub is None:
            return
        if self.use_stamped:
            msg = TwistStamped()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = 'base_link'
            msg.twist = cmd
            self.pub.publish(msg)
        else:
            self.pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoider()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
