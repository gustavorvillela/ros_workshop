// Aula 4 — color_masks
// Lê a câmera (/camera/image_raw), separa cada cor com uma máscara HSV e publica
//   /vision/mask/<cor>  máscara de cada cor (mono8: 255 onde a cor aparece, 0 no resto)
// O que fazer com as máscaras (achar os cilindros) fica para a Aula 5.
// Complete os TODO 1 a 6 (o 7 é extensão).
// Compile com: cd ~/workshop_ws && colcon build --packages-select robo_lp

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

class ColorMasks : public rclcpp::Node {
public:
  ColorMasks() : Node("color_masks") {
    // Parâmetros prontos. Os limites são lidos a cada imagem, então dá para ajustá-los
    // com o nó rodando: ros2 param set /color_masks verde "[45, 100, 50, 85, 255, 255]"
    declare_parameter("kernel_size", 5);    // px: tamanho do elemento da morfologia
    for (const auto & [cor, limites] : kCoresPadrao) {
      declare_parameter(cor, limites);
    }

    // TODO 1: para cada cor, criar em mask_pubs_[cor] um publisher de sensor_msgs::msg::Image
    //   no tópico "/vision/mask/" + cor, com fila de 10.

    // TODO 2: assinar "/camera/image_raw" com rclcpp::SensorDataQoS(), chamando on_image(msg).
    //   O callback recebe sensor_msgs::msg::Image::ConstSharedPtr.
  }

private:
  // Devolve a máscara (CV_8UC1) dos pixels de hsv dentro dos limites l.
  static cv::Mat mascara(const cv::Mat & hsv, const std::vector<int64_t> & l) {
    // TODO 3: se l[0] <= l[3], um único cv::inRange(hsv, cv::Scalar(mínimos), cv::Scalar(máximos), mask).
    //   Senão (vermelho), junte duas faixas com cv::bitwise_or:
    //   H de 0 até l[3]  e  H de l[0] até 179 (S e V iguais nas duas).
    (void)l;
    return cv::Mat::zeros(hsv.size(), CV_8UC1);
  }

  void on_image(const sensor_msgs::msg::Image::ConstSharedPtr & msg) {
    cv::Mat hsv;
    // TODO 4: converter a mensagem em cv::Mat BGR com cv_bridge::toCvShare(msg, "bgr8")->image
    //   e depois para HSV com cv::cvtColor(frame, hsv, cv::COLOR_BGR2HSV).
    if (hsv.empty()) return;   // apague esta linha quando fizer o TODO 4

    const int k = static_cast<int>(get_parameter("kernel_size").as_int());
    const cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(k, k));
    std::string pixels;

    for (const auto & [cor, padrao] : kCoresPadrao) {
      const auto limites = get_parameter(cor).as_integer_array();
      if (limites.size() != 6) {
        RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 5000, "%s: são 6 números", cor.c_str());
        continue;
      }
      cv::Mat mask = mascara(hsv, limites);

      // TODO 5: limpar a máscara com cv::morphologyEx(mask, mask, ...): primeiro cv::MORPH_OPEN
      //   (apaga pontinhos soltos), depois cv::MORPH_CLOSE (fecha furos), com kernel.

      // TODO 6: publicar a máscara em mask_pubs_[cor]:
      //   *cv_bridge::CvImage(msg->header, "mono8", mask).toImageMsg()
      //   O header igual ao da câmera (mesmo instante) é o que a Aula 5 usa para casar imagem e máscaras.

      // TODO 7 (extensão): contar os pixels brancos com cv::countNonZero(mask) e, se n > 0,
      //   acrescentar em pixels o texto "<cor>: <n> px" (separado por vírgula).
    }

    if (!pixels.empty()) {
      RCLCPP_INFO_THROTTLE(get_logger(), *get_clock(), 2000, "vejo %s", pixels.c_str());
    }
  }

  std::map<std::string, rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr> mask_pubs_;
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr sub_;
};

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ColorMasks>());
  rclcpp::shutdown();
  return 0;
}
