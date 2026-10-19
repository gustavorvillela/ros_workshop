// Nó que faz a tartaruga do turtlesim andar e desviar das paredes.
//   Assina:  /turtle1/pose     (turtlesim/msg/Pose)       -> onde a tartaruga está
//   Publica: /turtle1/cmd_vel  (geometry_msgs/msg/Twist)  -> velocidade da tartaruga
//
// Exercício da aula: complete os TODOs na ordem 1, 2, 3.
// A versão pronta está em desviador_turtlesim_solucao.cpp.

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
    // TODO 1: criar o publisher de turtle1/cmd_vel (geometry_msgs::msg::Twist)
    //         e o subscriber de turtle1/pose (turtlesim::msg::Pose) que chama pose_callback

    // TODO 3: declarar os parâmetros distancia, velocidade e velocidade_giro

    RCLCPP_INFO(get_logger(), "Desviador (turtlesim) iniciado");
  }

private:
  // Chamada toda vez que o turtlesim publica a pose da tartaruga (~60 vezes por segundo)
  void pose_callback(const turtlesim::msg::Pose::SharedPtr pose)
  {
    // TODO 2: perguntar parede_a_frente(*pose, DISTANCIA) e publicar:
    //   - parede à frente: girar no lugar (cmd.angular.z)
    //   - caminho livre: andar para frente (cmd.linear.x)
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

  // Valores fixos por enquanto. TODO 3: trocar por parâmetros
  static constexpr double DISTANCIA = 1.0;        // m
  static constexpr double VELOCIDADE = 1.5;       // m/s
  static constexpr double VELOCIDADE_GIRO = 1.5;  // rad/s

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
