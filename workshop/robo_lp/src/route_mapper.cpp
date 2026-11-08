// Aula 3 — route_mapper
// Faz o robô percorrer uma lista de pontos (waypoints) usando a odometria, para o
// Cartographer mapear a sala sozinho. Complete os TODO 1 a 8 (o 9 é extensão).
// Compile com: cd ~/workshop_ws && colcon build --packages-select robo_lp

#include <algorithm>
#include <cmath>
#include <vector>

#include "rclcpp/rclcpp.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "geometry_msgs/msg/twist.hpp"

using namespace std::chrono_literals;

class RouteMapper : public rclcpp::Node {
public:
  RouteMapper() : Node("route_mapper") {
    // TODO 1: declarar os parâmetros (declare_parameter) e guardar nos membros:
    //   waypoints (std::vector<double>, pares x, y no frame odom; padrão: quadrado de 6 m
    //   {6, 0, 6, 6, 0, 6, 0, 0}), v_max = 0.3, w_max = 0.5, tolerance = 0.10,
    //   k_lin = 0.5, k_ang = 1.5

    // TODO 2: converter o vetor de waypoints em route_ (cada par x, y vira um Point)

    // TODO 3: assinar /odom (nav_msgs::msg::Odometry) e, no callback,
    //   guardar x_, y_ e yaw_ e marcar have_odom_ = true.
    //   yaw a partir do quaternion q: atan2(2(w*z + x*y), 1 - 2(y*y + z*z))

    // TODO 4: criar o publisher de /cmd_vel (geometry_msgs::msg::Twist)

    // TODO 5: criar um timer de 100 ms que chama step()
  }

private:
  struct Point { double x, y; };

  void step() {
    geometry_msgs::msg::Twist cmd;  // começa zerado = robô parado

    // TODO 6: sem odometria ainda, ou com o percurso terminado (idx_ >= route_.size()),
    //   publicar cmd parado e sair. Avisar no log uma única vez (use done_).

    // TODO 7: calcular a distância até route_[idx_] (std::hypot) e o erro de rumo
    //   (ângulo até o ponto menos yaw_), normalizado com atan2(sin(e), cos(e)).

    // TODO 8: escolher a ação:
    //   - dist < tol_: avisar no log e passar ao próximo ponto (++idx_)
    //   - |erro| > 0.2 rad: girar no lugar, w = k_ang_ * erro
    //   - senão: andar, v = k_lin_ * dist, corrigindo o rumo com w = k_ang_ * erro
    //   Limite v a v_max_ e w a [-w_max_, w_max_] com std::min e std::clamp.

    cmd_pub_->publish(cmd);
  }

  // TODO 9 (extensão): assinar /scan e não andar se algo estiver a menos de 0,3 m.

  std::vector<Point> route_;
  size_t idx_ = 0;
  double x_ = 0, y_ = 0, yaw_ = 0;
  double v_max_ = 0, w_max_ = 0, tol_ = 0, k_lin_ = 0, k_ang_ = 0;
  bool have_odom_ = false, done_ = false;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_pub_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<RouteMapper>());
  rclcpp::shutdown();
  return 0;
}
