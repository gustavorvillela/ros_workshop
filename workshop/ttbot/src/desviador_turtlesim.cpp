// Plano B: a mesma ideia do desviador, no turtlesim (roda sem Gazebo e sem GPU).
//   Assina:  /turtle1/pose     (turtlesim/msg/Pose)       -> onde a tartaruga está
//   Publica: /turtle1/cmd_vel  (geometry_msgs/msg/Twist)  -> velocidade da tartaruga
//
// O turtlesim não tem laser: o "sensor" é olhar um ponto a `distancia` metros à frente
// e ver se ele cai fora da área livre (a janela vai de 0 a ~11 m nos dois eixos).

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
    pub_ = create_publisher<geometry_msgs::msg::Twist>("turtle1/cmd_vel", 10);
    sub_ = create_subscription<turtlesim::msg::Pose>(
      "turtle1/pose", 10,
      std::bind(&DesviadorTurtlesim::pose_callback, this, std::placeholders::_1));

    declare_parameter("distancia", 1.0);        // m
    declare_parameter("velocidade", 1.5);       // m/s
    declare_parameter("velocidade_giro", 1.5);  // rad/s

    RCLCPP_INFO(get_logger(), "Desviador (turtlesim) iniciado");
  }

private:
  // Chamada toda vez que o turtlesim publica a pose da tartaruga
  void pose_callback(const turtlesim::msg::Pose::SharedPtr pose)
  {
    const double d = get_parameter("distancia").as_double();
    const double x_frente = pose->x + d * std::cos(pose->theta);
    const double y_frente = pose->y + d * std::sin(pose->theta);

    geometry_msgs::msg::Twist cmd;
    if (fora_da_area(x_frente) || fora_da_area(y_frente)) {
      cmd.angular.z = get_parameter("velocidade_giro").as_double();  // parede à frente: gira
    } else {
      cmd.linear.x = get_parameter("velocidade").as_double();        // livre: anda para frente
    }
    pub_->publish(cmd);
  }

  static bool fora_da_area(double coordenada)
  {
    return coordenada < MARGEM || coordenada > LADO - MARGEM;
  }

  static constexpr double LADO = 11.0;   // tamanho da janela do turtlesim (m)
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
