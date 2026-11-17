"""Aula 6 — cylinder_follower.

Leva o robô até o cilindro de uma cor, usando as detecções da Aula 5 e dois PIDs:
  - angular: gira até o cilindro ficar no centro da imagem;
  - linear: anda até o cilindro ficar a 'distancia' metros da câmera.
Publica /cmd_vel e, para o rqt_plot, /pid/angular e /pid/linear com
[erro, P, I, D, saída].

Complete os TODO 1 a 5 (o 6 é extensão). Antes, complete o pid.py.
Rode com: ros2 run robo_py cylinder_follower --ros-args -p use_sim_time:=true -p cor:=verde
"""
import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo
from std_msgs.msg import Float64MultiArray
from vision_msgs.msg import Detection2DArray

from robo_py.pid import PID


class CylinderFollower(Node):

    def __init__(self):
        super().__init__('cylinder_follower')
        # Parâmetros prontos. Os ganhos são lidos a cada ciclo: dá para sintonizar com o nó
        # rodando, por exemplo: ros2 param set /cylinder_follower kd_ang 0.3
        self.declare_parameter('cor', 'verde')            # cilindro a seguir
        self.declare_parameter('distancia', 1.5)          # m: onde parar, medido da câmera
        self.declare_parameter('altura_cilindro', 1.0)    # m: altura real dos cilindros
        self.declare_parameter('kp_ang', 1.0)
        self.declare_parameter('ki_ang', 0.0)
        self.declare_parameter('kd_ang', 0.0)
        self.declare_parameter('kp_lin', 0.3)
        self.declare_parameter('ki_lin', 0.0)
        self.declare_parameter('kd_lin', 0.0)
        self.declare_parameter('alfa_d', 0.0)             # filtro da derivada (TODO 5 do pid.py)
        self.declare_parameter('v_max', 0.3)              # m/s
        self.declare_parameter('w_max', 0.6)              # rad/s
        self.declare_parameter('erro_ang_andar', 0.3)     # rad: só anda se o alvo estiver à frente
        self.declare_parameter('vies_angular', 0.0)       # rad/s somado ao comando: simula uma
                                                          # roda desalinhada (perturbação)
        self.declare_parameter('w_busca', 0.3)            # rad/s: giro quando não vê o alvo
        self.declare_parameter('timeout', 1.0)            # s sem detecção = alvo perdido

        self.pid_ang = PID(saida_max=0.6, integral_max=0.5)
        self.pid_lin = PID(saida_max=0.3, integral_max=2.0)
        self.fx = self.fy = self.cx0 = None   # da camera_info
        self.alvo = None                      # (cx, altura da caixa em px) da última detecção
        self.t_alvo = None                    # instante da última detecção do alvo
        self.t_anterior = None                # instante do ciclo de controle anterior
        self.chegou = False

        self.create_subscription(CameraInfo, '/camera/camera_info', self.on_info,
                                 qos_profile_sensor_data)
        self.dbg_ang = self.create_publisher(Float64MultiArray, '/pid/angular', 10)
        self.dbg_lin = self.create_publisher(Float64MultiArray, '/pid/linear', 10)

        # TODO 1: criar self.cmd_pub (Twist em '/cmd_vel', fila 10), assinar
        #   '/vision/detections' (Detection2DArray, fila 10) chamando self.on_detections e
        #   criar um timer de 0.05 s (20 Hz) chamando self.controle.

    def on_info(self, msg):
        self.fx, self.fy, self.cx0 = msg.k[0], msg.k[4], msg.k[2]

    def on_detections(self, msg):
        cor = self.get_parameter('cor').value
        # TODO 2: entre as detecções de msg.detections cuja classe
        #   (d.results[0].hypothesis.class_id) é a cor pedida, pegue a de caixa mais alta
        #   (d.bbox.size_y: a mais próxima). Se houver, guarde
        #   self.alvo = (d.bbox.center.position.x, d.bbox.size_y) e
        #   self.t_alvo = self.get_clock().now().

    def erros(self):
        """Devolve (erro angular em rad, erro de distância em m) para o alvo atual."""
        cx, altura_px = self.alvo
        # TODO 3: os dois erros, a partir do modelo de câmera pinhole.
        #   - angular: o ângulo do alvo em relação ao eixo da câmera, atan2(cx0 - cx, fx)
        #     (positivo = alvo à esquerda = girar para a esquerda, w > 0).
        #   - distância: um objeto de altura real H a uma distância Z aparece com
        #     h = fy * H / Z pixels; então Z = fy * altura_cilindro / altura_px.
        #     O erro é Z - distancia (positivo = longe = andar para a frente).
        return 0.0, 0.0

    def controle(self):
        agora = self.get_clock().now()
        dt = 0.0 if self.t_anterior is None else (agora - self.t_anterior).nanoseconds * 1e-9
        self.t_anterior = agora
        p = lambda nome: self.get_parameter(nome).value
        self.pid_ang.ajustar(p('kp_ang'), p('ki_ang'), p('kd_ang'))
        self.pid_lin.ajustar(p('kp_lin'), p('ki_lin'), p('kd_lin'))
        self.pid_ang.saida_max, self.pid_lin.saida_max = p('w_max'), p('v_max')
        self.pid_ang.alfa_d = self.pid_lin.alfa_d = p('alfa_d')
        cmd = Twist()

        perdido = (self.alvo is None or self.fx is None or
                   (agora - self.t_alvo).nanoseconds * 1e-9 > p('timeout'))
        # TODO 4: se perdido, gire no lugar para procurar (cmd.angular.z = w_busca) e
        #   zere a história dos dois PIDs com reset() (a integral acumulada com outro
        #   alvo, ou de muito tempo atrás, não serve mais).
        if perdido:
            pass
        else:
            erro_ang, erro_lin = self.erros()
            # TODO 5: cmd.angular.z = saída do pid_ang para erro_ang. Só ande se o alvo estiver
            #   à frente (|erro_ang| < erro_ang_andar): cmd.linear.x = saída do pid_lin para
            #   erro_lin; senão, linear fica 0 e chame self.pid_lin.reset() (não deixe a
            #   integral crescer parado).
            self.dbg_ang.publish(self.debug(self.pid_ang, erro_ang, cmd.angular.z))
            self.dbg_lin.publish(self.debug(self.pid_lin, erro_lin, cmd.linear.x))

            # TODO 6 (extensão): quando |erro_lin| < 0.05 m e |erro_ang| < 0.03 rad, escreva
            #   uma vez no log f'cheguei ao cilindro {cor}' (use self.chegou).

        # A perturbação entra depois do controlador, como um defeito do robô
        cmd.angular.z += p('vies_angular')
        if hasattr(self, 'cmd_pub'):
            self.cmd_pub.publish(cmd)

    @staticmethod
    def debug(pid, erro, saida):
        return Float64MultiArray(data=[float(erro), pid.p, pid.i, pid.d, float(saida)])


def main(args=None):
    rclpy.init(args=args)
    node = CylinderFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
