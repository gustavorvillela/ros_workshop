"""Aula 5 — cylinder_detector.

Recebe a imagem da câmera e as quatro máscaras do color_masks (Aula 4), casadas pelo
instante em que foram capturadas, acha cada cilindro em cada máscara e publica:
  /vision/detections  vision_msgs/Detection2DArray: cor, caixa e centro de cada cilindro
  /vision/annotated   a imagem crua da câmera, republicada com as caixas e os centroides

Complete os TODO 1 a 8 (o 9 é extensão).
Rode com: ros2 run robo_py cylinder_detector --ros-args -p use_sim_time:=true
"""
import math

import cv2
import message_filters
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, Image
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose

# A ordem importa: é a ordem em que as máscaras chegam no callback on_sync.
CORES = ['vermelho', 'verde', 'azul', 'amarelo']
# Cor (BGR) usada para desenhar cada cilindro na imagem anotada
COR_DESENHO = {
    'vermelho': (0, 0, 255),
    'verde': (0, 200, 0),
    'azul': (255, 0, 0),
    'amarelo': (0, 220, 255),
}


class CylinderDetector(Node):

    def __init__(self):
        super().__init__('cylinder_detector')
        self.declare_parameter('min_area', 200.0)   # px²: manchas menores são ignoradas
        self.bridge = CvBridge()
        self.fx = None   # distância focal e centro óptico, em pixels (TODO 9)
        self.cx0 = None

        # TODO 1: criar self.det_pub (Detection2DArray em '/vision/detections') e
        #   self.img_pub (Image em '/vision/annotated'), os dois com fila de 10.
        self.det_pub = None
        self.img_pub = None

        # TODO 2: casar a imagem com as quatro máscaras do mesmo instante (mesmo header.stamp).
        #   a) Crie uma lista subs com um message_filters.Subscriber(self, Image, tópico,
        #      qos_profile=qos_profile_sensor_data) para '/camera/image_raw' e, em seguida,
        #      um para cada f'/vision/mask/{cor}', na ordem de CORES.
        #   b) self.sync = message_filters.TimeSynchronizer(subs, 10)
        #   c) self.sync.registerCallback(self.on_sync)
        #   on_sync só é chamado quando chegam as 5 mensagens com o mesmo instante.

        # TODO 9 (extensão): assinar '/camera/camera_info' (CameraInfo) chamando self.on_info.

    def on_info(self, msg):
        # K = [fx 0 cx; 0 fy cy; 0 0 1], guardada por linhas em msg.k
        self.fx, self.cx0 = msg.k[0], msg.k[2]

    def detectar(self, mask):
        """Devolve uma lista de (cx, cy, x, y, w, h), uma por mancha da máscara."""
        min_area = self.get_parameter('min_area').value
        achados = []
        # TODO 4: achar os contornos externos das manchas brancas:
        #   contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #   e percorrer cada contorno c fazendo os TODO 5 a 7.
        # TODO 5: pular o contorno se cv2.contourArea(c) < min_area (ruído, cilindro muito longe).
        # TODO 6: o centroide da mancha, pelos momentos da imagem: m = cv2.moments(c),
        #   cx = m['m10'] / m['m00'] e cy = m['m01'] / m['m00'] (pule se m['m00'] == 0).
        #   m00 é a área; m10 e m01 são as somas de x e de y dos pixels.
        # TODO 7: a caixa: x, y, w, h = cv2.boundingRect(c), e achados.append((cx, cy, x, y, w, h)).
        return achados

    def on_sync(self, img_msg, *mask_msgs):
        # TODO 3: converter img_msg para BGR (self.bridge.imgmsg_to_cv2(img_msg, 'bgr8').copy(),
        #   a cópia é onde vamos desenhar) e criar deteccoes = Detection2DArray() com o
        #   header de img_msg.
        anotada, deteccoes = None, None
        if anotada is None:
            return   # remova estas duas linhas quando fizer o TODO 3
        resumo = []

        for cor, mask_msg in zip(CORES, mask_msgs):
            mask = self.bridge.imgmsg_to_cv2(mask_msg, desired_encoding='mono8')
            for (cx, cy, x, y, w, h) in self.detectar(mask):
                # TODO 8: para cada cilindro achado:
                #   a) montar um Detection2D d: d.header = img_msg.header, d.id = cor, uma hipótese
                #      hip = ObjectHypothesisWithPose() com hip.hypothesis.class_id = cor e
                #      hip.hypothesis.score = 1.0 em d.results; a caixa em d.bbox (o centro da
                #      caixa em d.bbox.center.position.x/.y, a largura e a altura em
                #      d.bbox.size_x/size_y, como float). Acrescente d em deteccoes.detections.
                #   b) desenhar em anotada: cv2.rectangle da caixa e cv2.circle de raio 4,
                #      preenchido (-1), no centroide, ambos com a cor COR_DESENHO[cor].
                rotulo = cor

                # TODO 9 (extensão): com self.fx e self.cx0 (do camera_info), o ângulo do
                #   cilindro em relação ao eixo da câmera é atan2(cx0 - cx, fx) (positivo à
                #   esquerda, como o yaw do robô). Acrescente-o em graus ao rotulo.
                cv2.putText(anotada, rotulo, (x, max(y - 6, 12)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COR_DESENHO[cor], 1)
                resumo.append(rotulo)

        # TODO 8 (continuação): publicar deteccoes em self.det_pub e a imagem anotada em
        #   self.img_pub (cv2_to_imgmsg com encoding 'bgr8' e o header de img_msg).

        if resumo:
            self.get_logger().info('cilindros: ' + ', '.join(resumo), throttle_duration_sec=2.0)


def main(args=None):
    rclpy.init(args=args)
    node = CylinderDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
