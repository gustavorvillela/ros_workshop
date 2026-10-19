// Nó que faz a tartaruga do turtlesim andar e desviar das paredes.
//   Assina:  /turtle1/pose     (turtlesim/msg/Pose)       -> onde a tartaruga está
//   Publica: /turtle1/cmd_vel  (geometry_msgs/msg/Twist)  -> velocidade da tartaruga
//
// Versão pronta do exercício em desviador_turtlesim.cpp.

#include <cmath>
#include <functional>
#include <memory>

#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
#include "turtlesim/msg/pose.hpp"

class DesviadorTurtlesim : public rclcpp::Node
{
public:
  DesviadorTurtlesim()
  : Node("desviador")
  {
    // (TODO 1) Publisher de turtle1/cmd_vel e subscriber de turtle1/pose
    pub_ = create_publisher<geometry_msgs::msg::Twist>("turtle1/cmd_vel", 10);
    sub_ = create_subscription<turtlesim::msg::Pose>(
      "turtle1/pose", 10,
      std::bind(&DesviadorTurtlesim::pose_callback, this, std::placeholders::_1));

    // (TODO 3) Parâmetros: nome e valor padrão; dá para mudar com o nó rodando
    declare_parameter("distancia", 1.0);        // m
    declare_parameter("velocidade", 1.5);       // m/s
    declare_parameter("velocidade_giro", 1.5);  // rad/s

    RCLCPP_INFO(get_logger(), "Desviador (turtlesim) iniciado");
  }

private:
  // Chamada toda vez que o turtlesim publica a pose da tartaruga (~60 vezes por segundo)
  void pose_callback(const turtlesim::msg::Pose::SharedPtr pose)
  {
    // (TODO 2) Decide o comando e publica
    geometry_msgs::msg::Twist cmd;
    if (parede_a_frente(*pose, get_parameter("distancia").as_double())) {
      cmd.angular.z = get_parameter("velocidade_giro").as_double();  // parede: gira no lugar
    } else {
      cmd.linear.x = get_parameter("velocidade").as_double();        // livre: anda para frente
    }
    pub_->publish(cmd);
  }

  // O turtlesim não tem laser: o "sensor" é olhar o ponto `distancia` metros à frente
  // da tartaruga e ver se ele cai fora da área livre da janela
  static bool parede_a_frente(const turtlesim::msg::Pose & pose, double distancia)
  {
    const double x = pose.x + distancia * std::cos(pose.theta);
    const double y = pose.y + distancia * std::sin(pose.theta);
    return x < MARGEM || x > LADO - MARGEM || y < MARGEM || y > LADO - MARGEM;
  }

  static constexpr double LADO = 11.0;   // a janela vai de 0 a ~11 m nos dois eixos
  static constexpr double MARGEM = 0.5;  // folga até a parede (m)

  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr pub_;
  rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr sub_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<DesviadorTurtlesim>());
  rclcpp::shutdown();
  return 0;
}
