// Aula 4 — color_masks
// Lê a câmera (/camera/image_raw), separa cada cor com uma máscara HSV e publica:
//   /vision/mask/<cor>  máscara de cada cor (mono8: 255 onde a cor aparece, 0 no resto)
//   /vision/debug       a imagem da câmera com o contorno e o centro de cada objeto achado
// Complete os TODO 1 a 8 (o 9 é extensão).
// Compile com: cd ~/workshop_ws && colcon build --packages-select robo_lp

#include <algorithm>
#include <map>
#include <string>
#include <utility>
#include <vector>

#include <opencv2/imgproc.hpp>

#include "cv_bridge/cv_bridge.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/image.hpp"

// Limites HSV de cada cor: {h_min, s_min, v_min, h_max, s_max, v_max}.
// No OpenCV, H vai de 0 a 179 e S e V de 0 a 255.
// Se h_min > h_max, a faixa de matiz dá a volta no 180 (é o caso do vermelho).
static const std::vector<std::pair<std::string, std::vector<int64_t>>> kCoresPadrao = {
  {"vermelho", {170, 120, 70, 10, 255, 255}},
  {"verde", {40, 100, 50, 80, 255, 255}},
  {"azul", {100, 120, 50, 130, 255, 255}},
  {"amarelo", {20, 120, 80, 35, 255, 255}},
};
// Cor (BGR) usada para desenhar cada detecção na imagem de depuração
static const std::map<std::string, cv::Scalar> kCorDesenho = {
  {"vermelho", {0, 0, 255}}, {"verde", {0, 200, 0}}, {"azul", {255, 0, 0}}, {"amarelo", {0, 220, 255}},
};

class ColorMasks : public rclcpp::Node {
public:
  ColorMasks() : Node("color_masks") {
    // Parâmetros prontos. Os limites são lidos a cada imagem, então dá para ajustá-los
    // com o nó rodando: ros2 param set /color_masks verde "[45, 100, 50, 85, 255, 255]"
    declare_parameter("min_area", 200.0);   // px²: contornos menores que isso são ignorados
    declare_parameter("kernel_size", 5);    // px: tamanho do elemento da morfologia
    for (const auto & [cor, limites] : kCoresPadrao) {
      declare_parameter(cor, limites);
    }

    // TODO 1: para cada cor, criar em mask_pubs_[cor] um publisher de sensor_msgs::msg::Image
    //   no tópico "/vision/mask/" + cor; e criar debug_pub_ no tópico "/vision/debug". Fila de 10.

    // TODO 2: assinar "/camera/image_raw" com rclcpp::SensorDataQoS(), chamando on_image(msg).
    //   O callback recebe sensor_msgs::msg::Image::ConstSharedPtr.
  }

private:
  // Devolve a máscara (CV_8UC1) dos pixels de hsv dentro dos limites l.
  static cv::Mat mascara(const cv::Mat & hsv, const std::vector<int64_t> & l) {
    // TODO 3: se l[0] <= l[3], um único cv::inRange(hsv, cv::Scalar(mínimos), cv::Scalar(máximos), mask).
    //   Senão (vermelho), junte duas faixas com cv::bitwise_or:
    //   H de 0 até l[3]  e  H de l[0] até 179 (S e V iguais nas duas).
    return cv::Mat::zeros(hsv.size(), CV_8UC1);
  }

  void on_image(const sensor_msgs::msg::Image::ConstSharedPtr & msg) {
    cv::Mat frame;
    // TODO 4: converter a mensagem em imagem BGR do OpenCV com
    //   cv_bridge::toCvShare(msg, "bgr8")->image, guardando em frame.
    if (frame.empty()) return;   // remova esta linha quando fizer o TODO 4
    cv::Mat hsv;
    //   ...e converter frame para HSV em hsv com cv::cvtColor(..., cv::COLOR_BGR2HSV).

    const int k = static_cast<int>(get_parameter("kernel_size").as_int());
    const double min_area = get_parameter("min_area").as_double();
    const cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(k, k));
    cv::Mat debug = frame.clone();

    for (const auto & [cor, padrao] : kCoresPadrao) {
      const auto limites = get_parameter(cor).as_integer_array();
      if (limites.size() != 6) {
        RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 5000, "%s: são 6 números", cor.c_str());
        continue;
      }
      cv::Mat mask = mascara(hsv, limites);

      // TODO 5: limpar a máscara com cv::morphologyEx: primeiro MORPH_OPEN (tira pontinhos soltos),
      //   depois MORPH_CLOSE (fecha buracos), os dois com kernel.

      // TODO 6: publicar a máscara em mask_pubs_[cor]:
      //   *cv_bridge::CvImage(msg->header, "mono8", mask).toImageMsg()

      // TODO 7: achar os contornos externos da máscara (cv::findContours com RETR_EXTERNAL e
      //   CHAIN_APPROX_SIMPLE). Para cada contorno com cv::contourArea >= min_area, desenhar em debug,
      //   com a cor kCorDesenho.at(cor): o retângulo de cv::boundingRect, um círculo no centro
      //   (cv::moments: x = m10/m00, y = m01/m00) e um texto com o nome da cor e a área (cv::putText).
      (void)min_area;   // remova esta linha quando usar min_area
    }

    // TODO 8: publicar debug em debug_pub_, com encoding "bgr8" e o mesmo header da mensagem.

    // TODO 9 (extensão): registrar no log, no máximo a cada 2 s (RCLCPP_INFO_THROTTLE),
    //   a área do maior objeto de cada cor que está sendo vista.
  }

  std::map<std::string, rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr> mask_pubs_;
  rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr debug_pub_;
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr sub_;
};

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ColorMasks>());
  rclcpp::shutdown();
  return 0;
}
