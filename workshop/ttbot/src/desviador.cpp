// Nó que faz o TurtleBot3 andar e desviar de obstáculos.
//   Assina:  /scan     (sensor_msgs/msg/LaserScan)  -> o que o laser enxerga
//   Publica: /cmd_vel  (geometry_msgs/msg/Twist)    -> velocidade do robô
//
// Exercício da aula: complete os TODOs na ordem 1, 2, 3.
// A versão pronta está em desviador_solucao.cpp.

#include <algorithm>
#include <cmath>
#include <functional>
#include <limits>
#include <memory>

#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"

class Desviador : public rclcpp::Node
{
public:
  Desviador()
  : Node("desviador")
  {
    // TODO 1: criar o publisher de /cmd_vel (geometry_msgs::msg::Twist)
    //         e o subscriber de /scan (sensor_msgs::msg::LaserScan) que chama scan_callback

    // TODO 3: declarar os parâmetros distancia, velocidade e velocidade_giro

    // Ao dar Ctrl+C, para o robô (o Gazebo continua executando o último comando recebido)
    get_node_base_interface()->get_context()->add_pre_shutdown_callback(
      [this]() {
        if (pub_) {pub_->publish(geometry_msgs::msg::Twist());}
      });

    RCLCPP_INFO(get_logger(), "Desviador iniciado");
  }

private:
  // Chamada toda vez que chega uma leitura nova do laser
  void scan_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg)
  {
    // TODO 2: medir a distância à frente com distancia_frente(*msg, CONE_GRAUS) e publicar:
    //   - obstáculo a menos de DISTANCIA: girar no lugar (cmd.angular.z)
    //   - caminho livre: andar para frente (cmd.linear.x)
  }

  // Menor leitura válida dentro de ±meio_cone_graus em torno da frente do robô (ângulo 0)
  static double distancia_frente(const sensor_msgs::msg::LaserScan & scan, double meio_cone_graus)
  {
    const double meio_cone = meio_cone_graus * M_PI / 180.0;
    double menor = std::numeric_limits<double>::infinity();

    for (size_t i = 0; i < scan.ranges.size(); ++i) {
      // Ângulo desta leitura, levado para o intervalo [-pi, pi]
      const double angulo = std::remainder(scan.angle_min + i * scan.angle_increment, 2.0 * M_PI);
      const double r = scan.ranges[i];
      // Fora de [range_min, range_max] (inclui inf e nan) é leitura inválida
      if (std::abs(angulo) <= meio_cone && r >= scan.range_min && r <= scan.range_max) {
        menor = std::min(menor, r);
      }
    }
    return menor;
  }

  static constexpr double CONE_GRAUS = 30.0;  // metade da abertura do "olhar" à frente

  // Valores fixos por enquanto. TODO 3: trocar por parâmetros
  static constexpr double DISTANCIA = 0.5;        // m
  static constexpr double VELOCIDADE = 0.15;      // m/s
  static constexpr double VELOCIDADE_GIRO = 0.8;  // rad/s

  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr pub_;
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr sub_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Desviador>());
  rclcpp::shutdown();
  return 0;
}
