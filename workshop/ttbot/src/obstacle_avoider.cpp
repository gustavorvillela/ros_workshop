// Aula 1 — obstacle_avoider
// Lê o lidar (/scan) e publica velocidades (/cmd_vel): anda para frente e
// gira no lugar quando há um obstáculo dentro de um cone à frente do robô.
// Complete os TODO. Compile com: cd ~/workshop_ws && colcon build --packages-select ttbot

#include <algorithm>
#include <cmath>
#include <limits>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "geometry_msgs/msg/twist_stamped.hpp"

class ObstacleAvoider : public rclcpp::Node {
public:
  ObstacleAvoider() : Node("obstacle_avoider") {
    // Parâmetros (a tarefa da Aula 1 é transformá-los em parâmetros; já deixamos prontos)
    max_speed_     = declare_parameter("max_speed", 0.15);      // m/s (o Burger vai até ~0.22)
    turn_speed_    = declare_parameter("turn_speed", 0.8);      // rad/s
    safe_distance_ = declare_parameter("safe_distance", 0.5);   // m
    cone_deg_      = declare_parameter("cone_deg", 30.0);       // meia-abertura do cone frontal
    // Confira o tipo esperado com: ros2 topic info -v /cmd_vel
    use_stamped_   = declare_parameter("use_stamped", true);    // TwistStamped (true) ou Twist (false)

    // TODO 1: criar o publisher de "cmd_vel".
    //   Se use_stamped_ for true, crie pub_stamped_ (geometry_msgs::msg::TwistStamped);
    //   senão, crie pub_ (geometry_msgs::msg::Twist). Fila de 10 mensagens.

    // TODO 2: assinar "scan" (sensor_msgs::msg::LaserScan) com QoS de sensor,
    //   rclcpp::SensorDataQoS(), chamando on_scan(*msg) no callback (use uma lambda).
  }

private:
  void on_scan(const sensor_msgs::msg::LaserScan & scan) {
    const double half_cone = cone_deg_ * M_PI / 180.0;
    float min_dist = std::numeric_limits<float>::infinity();

    // TODO 3: percorrer scan.ranges e guardar em min_dist a menor leitura válida
    //   dentro do cone frontal (|ângulo| <= half_cone).
    //   - ângulo do raio i: scan.angle_min + i * scan.angle_increment
    //   - o lidar do TurtleBot3 vai de 0 a 2*pi: normalize com atan2(sin(a), cos(a))
    //   - leitura válida: std::isfinite(r) e range_min <= r <= range_max
    (void)half_cone;  // remova estas duas linhas quando usar half_cone e scan
    (void)scan;

    geometry_msgs::msg::Twist cmd;
    // TODO 4: se min_dist < safe_distance_, girar no lugar (cmd.angular.z);
    //   senão, andar para frente (cmd.linear.x).
    (void)min_dist;   // remova esta linha quando usar min_dist

    publish(cmd);
  }

  // Pronto: publica cmd no tipo certo para o robô
  void publish(const geometry_msgs::msg::Twist & cmd) {
    if (use_stamped_) {
      if (!pub_stamped_) return;
      geometry_msgs::msg::TwistStamped msg;
      msg.header.stamp = now();
      msg.header.frame_id = "base_link";
      msg.twist = cmd;
      pub_stamped_->publish(msg);
    } else {
      if (!pub_) return;
      pub_->publish(cmd);
    }
  }

  double max_speed_, turn_speed_, safe_distance_, cone_deg_;
  bool use_stamped_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr pub_;
  rclcpp::Publisher<geometry_msgs::msg::TwistStamped>::SharedPtr pub_stamped_;
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr sub_;
};

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ObstacleAvoider>());
  rclcpp::shutdown();
  return 0;
}
