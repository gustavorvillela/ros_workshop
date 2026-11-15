"""Aula 4 — color_masks.

Lê a câmera (/camera/image_raw), separa cada cor com uma máscara HSV e publica
/vision/mask/<cor>: mono8, 255 onde a cor aparece e 0 no resto.
O que fazer com as máscaras (achar os cilindros) fica para a Aula 5.

Complete os TODO 1 a 6 (o 7 é extensão).
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


class ColorMasks(Node):

    def __init__(self):
        super().__init__('color_masks')
        # Parâmetros prontos. Os limites são lidos a cada imagem, então dá para ajustá-los
        # com o nó rodando: ros2 param set /color_masks verde "[45, 100, 50, 85, 255, 255]"
        self.declare_parameter('kernel_size', 5)    # px: tamanho do elemento da morfologia
        for cor, limites in CORES_PADRAO.items():
            self.declare_parameter(cor, limites)
        self.bridge = CvBridge()

        # TODO 1: criar self.mask_pubs, um dicionário {cor: publisher de Image} com os tópicos
        #   f'/vision/mask/{cor}' e fila de 10.
        self.mask_pubs = {}

        # TODO 2: assinar '/camera/image_raw' (Image) com qos_profile_sensor_data,
        #   chamando self.on_image.

    def mascara(self, hsv, limites):
        """Devolve a máscara (uint8, 0 ou 255) dos pixels de hsv dentro dos limites."""
        h_min, s_min, v_min, h_max, s_max, v_max = limites
        # TODO 3: se h_min <= h_max, um único cv2.inRange(hsv, mínimos, máximos).
        #   Senão (vermelho), junte com cv2.bitwise_or duas faixas:
        #   H de 0 até h_max  e  H de h_min até 179 (S e V iguais nas duas).
        return np.zeros(hsv.shape[:2], np.uint8)

    def on_image(self, msg):
        # TODO 4: converter a mensagem em imagem BGR do OpenCV com
        #   self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8'), e depois para HSV
        #   com cv2.cvtColor(..., cv2.COLOR_BGR2HSV).
        hsv = None
        if hsv is None:
            return   # remova estas duas linhas quando fizer o TODO 4

        k = int(self.get_parameter('kernel_size').value)
        kernel = np.ones((k, k), np.uint8)
        pixels = []

        for cor in CORES_PADRAO:
            limites = self.get_parameter(cor).value
            if len(limites) != 6:
                self.get_logger().warn(f'{cor}: são 6 números', throttle_duration_sec=5.0)
                continue
            mask = self.mascara(hsv, limites)

            # TODO 5: limpar a máscara com cv2.morphologyEx: primeiro cv2.MORPH_OPEN
            #   (apaga pontinhos soltos), depois cv2.MORPH_CLOSE (fecha furos), com kernel.

            # TODO 6: publicar a máscara em self.mask_pubs[cor], convertida com
            #   self.bridge.cv2_to_imgmsg(mask, encoding='mono8') e com o mesmo header de msg.
            #   O header igual (mesmo instante) é o que a Aula 5 usa para casar imagem e máscaras.

            # TODO 7 (extensão): contar os pixels brancos da máscara com cv2.countNonZero
            #   e guardar em pixels o texto f'{cor}: {n} px' quando n > 0.

        if pixels:
            self.get_logger().info('vejo ' + ', '.join(pixels), throttle_duration_sec=2.0)


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
