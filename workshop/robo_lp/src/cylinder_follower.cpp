// Aula 6 — cylinder_follower
// Leva o robô até o cilindro de uma cor, usando as detecções da Aula 5 e dois PIDs:
//   - angular: gira até o cilindro ficar no centro da imagem;
//   - linear: anda até o cilindro ficar a 'distancia' metros da câmera.
// Publica /cmd_vel e, para o rqt_plot, /pid/angular e /pid/linear com [erro, P, I, D, saída].
// Complete os TODO 1 a 5 (o 6 é extensão). Antes, complete o include/robo_lp/pid.hpp.
// Compile com: cd ~/workshop_ws && colcon build --packages-select robo_lp

#include <algorithm>
#include <cmath>
#include <optional>
#include <string>

#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/create_timer.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/camera_info.hpp"
#include "std_msgs/msg/float64_multi_array.hpp"
#include "vision_msgs/msg/detection2_d_array.hpp"

#include "robo_lp/pid.hpp"

using namespace std::chrono_literals;
using vision_msgs::msg::Detection2DArray;

class CylinderFollower : public rclcpp::Node {
public:
  CylinderFollower() : Node("cylinder_follower"), pid_ang_(0.6, 0.5), pid_lin_(0.3, 2.0) {
    // Parâmetros prontos. Os ganhos são lidos a cada ciclo: dá para sintonizar com o nó
    // rodando, por exemplo: ros2 param set /cylinder_follower kd_ang 0.3
    declare_parameter("cor", "verde");            // cilindro a seguir
    declare_parameter("distancia", 1.5);          // m: onde parar, medido da câmera
    declare_parameter("altura_cilindro", 1.0);    // m: altura real dos cilindros
    declare_parameter("kp_ang", 1.0);
    declare_parameter("ki_ang", 0.0);
    declare_parameter("kd_ang", 0.0);
    declare_parameter("kp_lin", 0.3);
    declare_parameter("ki_lin", 0.0);
    declare_parameter("kd_lin", 0.0);
    declare_parameter("alfa_d", 0.0);             // filtro da derivada (TODO 5 do pid.hpp)
    declare_parameter("v_max", 0.3);              // m/s
    declare_parameter("w_max", 0.6);              // rad/s
    declare_parameter("erro_ang_andar", 0.3);     // rad: só anda se o alvo estiver à frente
    declare_parameter("vies_angular", 0.0);       // rad/s somado ao comando: simula uma roda
                                                  // desalinhada (perturbação)
    declare_parameter("w_busca", 0.3);            // rad/s: giro quando não vê o alvo
    declare_parameter("timeout", 1.0);            // s sem detecção = alvo perdido

    info_sub_ = create_subscription<sensor_msgs::msg::CameraInfo>(
      "/camera/camera_info", rclcpp::SensorDataQoS(),
      [this](sensor_msgs::msg::CameraInfo::ConstSharedPtr m) { fx_ = m->k[0]; fy_ = m->k[4]; cx0_ = m->k[2]; });
    dbg_ang_ = create_publisher<std_msgs::msg::Float64MultiArray>("/pid/angular", 10);
    dbg_lin_ = create_publisher<std_msgs::msg::Float64MultiArray>("/pid/linear", 10);

    // TODO 1: criar cmd_pub_ (geometry_msgs::msg::Twist em "/cmd_vel", fila 10), assinar
    //   "/vision/detections" (Detection2DArray, fila 10) chamando on_detections(msg) e criar
    //   um timer de 50ms (20 Hz) no relógio do nó (o da simulação) chamando controle():
    //   timer_ = rclcpp::create_timer(this, get_clock(), 50ms, [this]() { controle(); });
  }

private:
  struct Alvo { double cx, altura_px; };

  void on_detections(const Detection2DArray::ConstSharedPtr & msg) {
    const std::string cor = get_parameter("cor").as_string();
    // TODO 2: entre as detecções de msg->detections cuja classe
    //   (d.results[0].hypothesis.class_id) é a cor pedida, pegue a de caixa mais alta
    //   (d.bbox.size_y: a mais próxima). Se houver, guarde
    //   alvo_ = Alvo{d.bbox.center.position.x, d.bbox.size_y} e t_alvo_ = now().
    (void)msg;
    (void)cor;
  }

  // Devolve {erro angular em rad, erro de distância em m} para o alvo atual.
  std::pair<double, double> erros() const {
    const double cx = alvo_->cx, altura_px = alvo_->altura_px;
    // TODO 3: os dois erros, a partir do modelo de câmera pinhole.
    //   - angular: o ângulo do alvo em relação ao eixo da câmera, atan2(cx0_ - cx, fx_)
    //     (positivo = alvo à esquerda = girar para a esquerda, w > 0).
    //   - distância: um objeto de altura real H a uma distância Z aparece com
    //     h = fy * H / Z pixels; então Z = fy_ * altura_cilindro / altura_px.
    //     O erro é Z - distancia (positivo = longe = andar para a frente).
    (void)cx;
    (void)altura_px;
    return {0.0, 0.0};
  }

  double par(const std::string & nome) const { return get_parameter(nome).as_double(); }

  void controle() {
    const rclcpp::Time agora = now();
    const double dt = t_anterior_ ? (agora - *t_anterior_).seconds() : 0.0;
    t_anterior_ = agora;
    pid_ang_.ajustar(par("kp_ang"), par("ki_ang"), par("kd_ang"));
    pid_lin_.ajustar(par("kp_lin"), par("ki_lin"), par("kd_lin"));
    pid_ang_.saida_max = par("w_max");
    pid_lin_.saida_max = par("v_max");
    pid_ang_.alfa_d = pid_lin_.alfa_d = par("alfa_d");
    geometry_msgs::msg::Twist cmd;

    const bool perdido = !alvo_ || fx_ <= 0.0 || (agora - t_alvo_).seconds() > par("timeout");
    // TODO 4: se perdido, gire no lugar para procurar (cmd.angular.z = w_busca) e zere a
    //   história dos dois PIDs com reset() (a integral acumulada com outro alvo, ou de muito
    //   tempo atrás, não serve mais).
    if (perdido) {
    } else {
      const auto [erro_ang, erro_lin] = erros();
      // TODO 5: cmd.angular.z = saída do pid_ang_ para erro_ang. Só ande se o alvo estiver à
      //   frente (|erro_ang| < erro_ang_andar): cmd.linear.x = saída do pid_lin_ para erro_lin;
      //   senão, linear fica 0 e chame pid_lin_.reset() (não deixe a integral crescer parado).
      dbg_ang_->publish(debug(pid_ang_, erro_ang, cmd.angular.z));
      dbg_lin_->publish(debug(pid_lin_, erro_lin, cmd.linear.x));

      // TODO 6 (extensão): quando |erro_lin| < 0.05 m e |erro_ang| < 0.03 rad, escreva uma vez
      //   no log "cheguei ao cilindro <cor>" (use chegou_).
    }

    // A perturbação entra depois do controlador, como um defeito do robô
    cmd.angular.z += par("vies_angular");
    if (cmd_pub_) cmd_pub_->publish(cmd);
  }

  static std_msgs::msg::Float64MultiArray debug(const PID & pid, double erro, double saida) {
    std_msgs::msg::Float64MultiArray m;
    m.data = {erro, pid.p, pid.i, pid.d, saida};
    return m;
  }

  PID pid_ang_, pid_lin_;
  double fx_ = 0.0, fy_ = 0.0, cx0_ = 0.0;   // da camera_info
  std::optional<Alvo> alvo_;                 // última detecção do alvo
  rclcpp::Time t_alvo_;                      // instante da última detecção do alvo
  std::optional<rclcpp::Time> t_anterior_;   // instante do ciclo de controle anterior
  bool chegou_ = false;

  rclcpp::Subscription<sensor_msgs::msg::CameraInfo>::SharedPtr info_sub_;
  rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr dbg_ang_, dbg_lin_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_pub_;
  rclcpp::Subscription<Detection2DArray>::SharedPtr det_sub_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CylinderFollower>());
  rclcpp::shutdown();
  return 0;
}
