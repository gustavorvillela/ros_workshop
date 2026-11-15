"""Aula 4 — color_masks.

Lê a câmera (/camera/image_raw), separa cada cor com uma máscara HSV e publica:
  /vision/mask/<cor>  máscara de cada cor (mono8: 255 onde a cor aparece, 0 no resto)
  /vision/debug       a imagem da câmera com o contorno e o centro de cada objeto achado
Complete os TODO 1 a 8 (o 9 é extensão).
Rode com: ros2 run robo_py color_masks --ros-args -p use_sim_time:=true
"""
import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image

# Limites HSV de cada cor, no formato [h_min, s_min, v_min, h_max, s_max, v_max].
# No OpenCV, H vai de 0 a 179 e S e V de 0 a 255.
# Se h_min > h_max, a faixa de matiz dá a volta no 180 (é o caso do vermelho).
CORES_PADRAO = {
    'vermelho': [170, 120, 70, 10, 255, 255],
    'verde': [40, 100, 50, 80, 255, 255],
    'azul': [100, 120, 50, 130, 255, 255],
    'amarelo': [20, 120, 80, 35, 255, 255],
}
# Cor (BGR) usada para desenhar cada detecção na imagem de depuração
COR_DESENHO = {
    'vermelho': (0, 0, 255),
    'verde': (0, 200, 0),
    'azul': (255, 0, 0),
    'amarelo': (0, 220, 255),
}


class ColorMasks(Node):

    def __init__(self):
        super().__init__('color_masks')
        # Parâmetros prontos. Os limites são lidos a cada imagem, então dá para ajustá-los
        # com o nó rodando: ros2 param set /color_masks verde "[45, 100, 50, 85, 255, 255]"
        self.declare_parameter('min_area', 200.0)   # px²: contornos menores são ignorados
        self.declare_parameter('kernel_size', 5)    # px: tamanho do elemento da morfologia
        for cor, limites in CORES_PADRAO.items():
            self.declare_parameter(cor, limites)
        self.bridge = CvBridge()

        # TODO 1: criar self.mask_pubs, um dicionário {cor: publisher de Image} com os tópicos
        #   f'/vision/mask/{cor}', e self.debug_pub no tópico '/vision/debug'. Fila de 10.
        self.mask_pubs = {}
        self.debug_pub = None

        # TODO 2: assinar '/camera/image_raw' (Image) com qos_profile_sensor_data,
        #   chamando self.on_image. Guarde em self.sub.

    def mascara(self, hsv, limites):
        """Devolve a máscara (uint8, 0 ou 255) dos pixels de hsv dentro dos limites."""
        h_min, s_min, v_min, h_max, s_max, v_max = limites
        # TODO 3: se h_min <= h_max, um único cv2.inRange(hsv, mínimos, máximos).
        #   Senão (vermelho), junte duas faixas com cv2.bitwise_or:
        #   H de 0 até h_max  e  H de h_min até 179 (S e V iguais nas duas).
        return np.zeros(hsv.shape[:2], np.uint8)

    def on_image(self, msg):
        # TODO 4: converter a mensagem em imagem BGR do OpenCV com
        #   self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8'), e depois para HSV
        #   com cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).
        frame = None
        hsv = None
        if frame is None:
            return   # remova estas duas linhas quando fizer o TODO 4

        k = int(self.get_parameter('kernel_size').value)
        min_area = self.get_parameter('min_area').value
        kernel = np.ones((k, k), np.uint8)
        debug = frame.copy()

        for cor in CORES_PADRAO:
            limites = self.get_parameter(cor).value
            if len(limites) != 6:
                self.get_logger().warn(f'{cor}: são 6 números', throttle_duration_sec=5.0)
                continue
            mask = self.mascara(hsv, limites)

            # TODO 5: limpar a máscara com cv2.morphologyEx: primeiro cv2.MORPH_OPEN
            #   (tira pontinhos soltos), depois cv2.MORPH_CLOSE (fecha buracos), os dois com kernel.

            # TODO 6: publicar a máscara em self.mask_pubs[cor], convertida com
            #   self.bridge.cv2_to_imgmsg(mask, encoding='mono8') e com o mesmo header de msg.

            # TODO 7: achar os contornos externos da máscara com
            #   cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE).
            #   Para cada contorno com cv2.contourArea >= min_area, desenhar em debug, com a cor
            #   COR_DESENHO[cor]: o retângulo de cv2.boundingRect, um círculo no centro
            #   (cv2.moments: x = m10/m00, y = m01/m00) e um texto com a cor e a área (cv2.putText).

        # TODO 8: publicar debug em self.debug_pub, com encoding 'bgr8' e o mesmo header de msg.

        # TODO 9 (extensão): registrar no log, no máximo a cada 2 s
        #   (self.get_logger().info(..., throttle_duration_sec=2.0)), a área do maior
        #   objeto de cada cor que está sendo vista.


def main(args=None):
    rclpy.init(args=args)
    node = ColorMasks()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
