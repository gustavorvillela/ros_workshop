// Nó que faz o TurtleBot3 andar e desviar de obstáculos.
//   Assina:  /scan     (sensor_msgs/msg/LaserScan)  -> o que o laser enxerga
//   Publica: /cmd_vel  (geometry_msgs/msg/Twist)    -> velocidade do robô
//
// Versão pronta do exercício em desviador.cpp.

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
    // (TODO 1) Publisher de /cmd_vel e subscriber de /scan
    pub_ = create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);
    sub_ = create_subscription<sensor_msgs::msg::LaserScan>(
      "scan", 10,
      std::bind(&Desviador::scan_callback, this, std::placeholders::_1));

    // (TODO 3) Parâmetros: nome e valor padrão; dá para mudar com o nó rodando
    declare_parameter("distancia", 0.5);        // m
    declare_parameter("velocidade", 0.15);      // m/s
    declare_parameter("velocidade_giro", 0.8);  // rad/s

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
    // (TODO 2) Decide o comando e publica
    const double dist = distancia_frente(*msg, CONE_GRAUS);

    geometry_msgs::msg::Twist cmd;
    if (dist < get_parameter("distancia").as_double()) {
      cmd.angular.z = get_parameter("velocidade_giro").as_double();  // obstáculo: gira no lugar
    } else {
      cmd.linear.x = get_parameter("velocidade").as_double();        // livre: anda para frente
    }
    pub_->publish(cmd);
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
