#include <chrono>
#include <memory>
#include <string>
#include <algorithm>
#include <iostream>

#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"

using namespace std::chrono_literals;

class TurtleBotMover : public rclcpp::Node
{
public:
  TurtleBotMover(double speed, const std::string & direction, double duration)
  : Node("turtlebot_mover"), speed_(speed), direction_(direction), duration_(duration)
  {
    // Inicia o publisher no tópico de velocidade do ttbot
    publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("/turtle1/cmd_vel", 10);

    // Publica o comando a cada 20ms (50 Hz)
    timer_ = this->create_wall_timer(20ms, std::bind(&TurtleBotMover::control_loop, this));

    start_time_ = this->now();

    RCLCPP_INFO(this->get_logger(), "Iniciando movimento: direcao='%s', velocidade=%.2f, duracao=%.2f segundos", direction_.c_str(), speed_, duration_);
  }

private:
  void control_loop()
  {
    auto elapsed_time = (this->now() - start_time_).seconds();

    // Quando atingir o tempo estipulado, envia comando de parada e encerra
    if (elapsed_time >= duration_) {
      publish_stop();
      RCLCPP_INFO(this->get_logger(), "Tempo limite atingido. TurtleBot parado.");
      timer_->cancel();
      rclcpp::shutdown();
      return;
    }

    geometry_msgs::msg::Twist msg;
    std::string dir = direction_;
    std::transform(dir.begin(), dir.end(), dir.begin(), ::tolower);

    // Mapeamento das direções
    if (dir == "fw") {
      msg.linear.x = speed_;
    } else if (dir == "bw") {
      msg.linear.x = -speed_;
    } else if (dir == "ccw") {
      msg.angular.z = speed_;
    } else if (dir == "cw") {
      msg.angular.z = -speed_;
    } else {
      RCLCPP_WARN_ONCE(
        this->get_logger(),
        "Direcao '%s' invalida. Use: fw, bw, ccw ou cw.",
        dir.c_str());
    }

    publisher_->publish(msg);
  }

  void publish_stop()
  {
    geometry_msgs::msg::Twist stop_msg;
    stop_msg.linear.x = 0.0;
    stop_msg.angular.z = 0.0;
    publisher_->publish(stop_msg);
  }

  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Time start_time_;

  double speed_;
  std::string direction_;
  double duration_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);

  // Filtra argumentos internos do ROS (--ros-args) mantendo os parâmetros informados pelo usuário
  auto non_ros_args = rclcpp::remove_ros_arguments(argc, argv);

  if (non_ros_args.size() < 4) {
    std::cout << "\nUso correto: ros2 run <pacote> move_ttbot <velocidade> <direcao> <duracao_segundos>\n" << std::endl;
    std::cout << "Exemplo:    ros2 run meu_pacote move_turtlebot 1 fw 5.0\n" << std::endl;
    std::cout << "Direcoes aceitas: fw, bw, ccw, cw\n" << std::endl;
    rclcpp::shutdown();
    return 1;
  }

  double speed = std::stod(non_ros_args[1]);
  std::string direction = non_ros_args[2];
  double duration = std::stod(non_ros_args[3]);

  auto node = std::make_shared<TurtleBotMover>(speed, direction, duration);
  rclcpp::spin(node);
  return 0;
}