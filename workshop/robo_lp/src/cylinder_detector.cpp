// Aula 5 — cylinder_detector
// Recebe a imagem da câmera e as quatro máscaras do color_masks (Aula 4), casadas pelo
// instante em que foram capturadas, acha cada cilindro em cada máscara e publica:
//   /vision/detections  vision_msgs/Detection2DArray: cor, caixa e centro de cada cilindro
//   /vision/annotated   a imagem crua da câmera, republicada com as caixas e os centroides
// Complete os TODO 1 a 8 (o 9 é extensão).
// Compile com: cd ~/workshop_ws && colcon build --packages-select robo_lp

#include <algorithm>
#include <array>
#include <cmath>
#include <functional>
#include <map>
#include <memory>
#include <string>
#include <vector>

#include <opencv2/imgproc.hpp>

#include "cv_bridge/cv_bridge.hpp"
#include "message_filters/subscriber.hpp"
#include "message_filters/time_synchronizer.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/camera_info.hpp"
#include "sensor_msgs/msg/image.hpp"
#include "vision_msgs/msg/detection2_d_array.hpp"

using sensor_msgs::msg::Image;
using vision_msgs::msg::Detection2DArray;

// A ordem importa: é a ordem em que as máscaras chegam no callback on_sync.
static const std::array<std::string, 4> kCores = {"vermelho", "verde", "azul", "amarelo"};
// Cor (BGR) usada para desenhar cada cilindro na imagem anotada
static const std::map<std::string, cv::Scalar> kCorDesenho = {
  {"vermelho", {0, 0, 255}}, {"verde", {0, 200, 0}}, {"azul", {255, 0, 0}}, {"amarelo", {0, 220, 255}},
};

// Um cilindro achado numa máscara: centroide (cx, cy) e caixa
struct Achado {
  double cx, cy;
  cv::Rect caixa;
};

class CylinderDetector : public rclcpp::Node {
public:
  // Imagem + 4 máscaras, casadas pelo header.stamp exato
  using Sync = message_filters::TimeSynchronizer<Image, Image, Image, Image, Image>;

  CylinderDetector() : Node("cylinder_detector") {
    declare_parameter("min_area", 200.0);   // px²: manchas menores são ignoradas

    // TODO 1: criar det_pub_ (Detection2DArray em "/vision/detections") e img_pub_
    //   (Image em "/vision/annotated"), os dois com fila de 10.

    // TODO 2: casar a imagem com as quatro máscaras do mesmo instante (mesmo header.stamp).
    //   a) img_sub_.subscribe(this, "/camera/image_raw", rmw_qos_profile_sensor_data);
    //      e mask_sub_[i].subscribe(...) com "/vision/mask/" + kCores[i], para i de 0 a 3.
    //   b) sync_ = std::make_shared<Sync>(img_sub_, mask_sub_[0], ..., mask_sub_[3], 10);
    //   c) sync_->registerCallback(std::bind(&CylinderDetector::on_sync, this,
    //        std::placeholders::_1, ..., std::placeholders::_5));
    //   on_sync só é chamado quando chegam as 5 mensagens com o mesmo instante.

    // TODO 9 (extensão): assinar "/camera/camera_info" (sensor_msgs::msg::CameraInfo) com
    //   rclcpp::SensorDataQoS() e guardar fx_ = msg->k[0] e cx0_ = msg->k[2]
    //   (K = [fx 0 cx; 0 fy cy; 0 0 1], guardada por linhas em msg->k).
  }

private:
  // Devolve um Achado por mancha branca da máscara.
  std::vector<Achado> detectar(const cv::Mat & mask) {
    const double min_area = get_parameter("min_area").as_double();
    std::vector<Achado> achados;
    // TODO 4: achar os contornos externos das manchas brancas:
    //   std::vector<std::vector<cv::Point>> contornos;
    //   cv::findContours(mask, contornos, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
    //   e percorrer cada contorno c fazendo os TODO 5 a 7.
    // TODO 5: pular o contorno se cv::contourArea(c) < min_area (ruído, cilindro muito longe).
    // TODO 6: o centroide da mancha, pelos momentos da imagem: cv::Moments m = cv::moments(c);
    //   cx = m.m10 / m.m00 e cy = m.m01 / m.m00 (pule se m.m00 == 0).
    //   m00 é a área; m10 e m01 são as somas de x e de y dos pixels.
    // TODO 7: a caixa é cv::boundingRect(c); guarde achados.push_back({cx, cy, caixa}).
    (void)mask;
    (void)min_area;
    return achados;
  }

  void on_sync(const Image::ConstSharedPtr & img,
               const Image::ConstSharedPtr & m0, const Image::ConstSharedPtr & m1,
               const Image::ConstSharedPtr & m2, const Image::ConstSharedPtr & m3) {
    const std::array<Image::ConstSharedPtr, 4> masks = {m0, m1, m2, m3};
    cv::Mat anotada;
    Detection2DArray deteccoes;
    // TODO 3: converter img para BGR numa cópia onde vamos desenhar:
    //   anotada = cv_bridge::toCvCopy(img, "bgr8")->image;  e deteccoes.header = img->header.
    if (anotada.empty()) return;   // apague esta linha quando fizer o TODO 3
    std::string resumo;

    for (size_t i = 0; i < kCores.size(); ++i) {
      const std::string & cor = kCores[i];
      const cv::Scalar & desenho = kCorDesenho.at(cor);
      const cv::Mat mask = cv_bridge::toCvShare(masks[i], "mono8")->image;
      for (const auto & a : detectar(mask)) {
        const cv::Rect & r = a.caixa;
        // TODO 8: para cada cilindro achado:
        //   a) montar um vision_msgs::msg::Detection2D d: d.header = img->header, d.id = cor,
        //      uma vision_msgs::msg::ObjectHypothesisWithPose hip com hip.hypothesis.class_id = cor
        //      e hip.hypothesis.score = 1.0 em d.results; a caixa em d.bbox (o centro da caixa em
        //      d.bbox.center.position.x/.y, a largura e a altura em d.bbox.size_x/size_y).
        //      Acrescente d em deteccoes.detections.
        //   b) desenhar em anotada: cv::rectangle(anotada, r, desenho, 2) e um cv::circle de raio 4,
        //      preenchido (-1), no centroide (a.cx, a.cy).
        std::string rotulo = cor;
        (void)r;

        // TODO 9 (extensão): com fx_ e cx0_ (do camera_info), o ângulo do cilindro em relação ao
        //   eixo da câmera é atan2(cx0_ - a.cx, fx_) (positivo à esquerda, como o yaw do robô).
        //   Acrescente-o em graus ao rotulo.
        cv::putText(anotada, rotulo, cv::Point(r.x, std::max(r.y - 6, 12)),
                    cv::FONT_HERSHEY_SIMPLEX, 0.5, desenho, 1);
        resumo += (resumo.empty() ? "" : ", ") + rotulo;
      }
    }

    // TODO 8 (continuação): publicar deteccoes em det_pub_ e a imagem anotada em img_pub_:
    //   *cv_bridge::CvImage(img->header, "bgr8", anotada).toImageMsg()

    if (!resumo.empty()) {
      RCLCPP_INFO_THROTTLE(get_logger(), *get_clock(), 2000, "cilindros: %s", resumo.c_str());
    }
  }

  rclcpp::Publisher<Detection2DArray>::SharedPtr det_pub_;
  rclcpp::Publisher<Image>::SharedPtr img_pub_;
  message_filters::Subscriber<Image> img_sub_;
  std::array<message_filters::Subscriber<Image>, 4> mask_sub_;
  std::shared_ptr<Sync> sync_;
  rclcpp::Subscription<sensor_msgs::msg::CameraInfo>::SharedPtr info_sub_;
  double fx_ = 0.0, cx0_ = 0.0;   // distância focal e centro óptico, em pixels (TODO 9)
};

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CylinderDetector>());
  rclcpp::shutdown();
  return 0;
}
