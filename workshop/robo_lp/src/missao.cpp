// Aula 7 — missao
// Usa os cilindros como waypoints: manda o cylinder_follower (Aula 6) até cada cor da
// 'sequencia', espera ele chegar, faz uma pausa e passa para a próxima. No fim, para o robô.
// Enquanto isso o Cartographer (Aula 3) faz o mapa.
// O nó não comanda as rodas: ele só muda o parâmetro 'cor' do cylinder_follower, por meio do
// serviço de parâmetros dele, e acompanha os erros que o follower publica em /pid/angular e
// /pid/linear para saber quando o robô chegou.
// Complete os TODO 1 a 5 (o 6 é extensão).
// Compile com: cd ~/workshop_ws && colcon build --packages-select robo_lp

#include <cmath>
#include <optional>
#include <string>
#include <utility>
#include <vector>

#include "rclcpp/create_timer.hpp"
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float64_multi_array.hpp"

using namespace std::chrono_literals;
using std_msgs::msg::Float64MultiArray;

class Missao : public rclcpp::Node {
public:
  Missao() : Node("missao") {
    declare_parameter("sequencia", std::vector<std::string>{"verde", "azul", "amarelo", "vermelho"});
    declare_parameter("tol_lin", 0.10);          // m: erro de distância aceito na chegada
    declare_parameter("tol_ang", 0.05);          // rad: erro angular aceito na chegada
    declare_parameter("tempo_estavel", 1.0);     // s dentro da tolerância para valer
    declare_parameter("pausa", 2.0);             // s parado em cada cilindro
    declare_parameter("tempo_max", 180.0);       // s por cilindro (TODO 6)
    declare_parameter("w_busca", 0.3);           // rad/s: giro de busca do follower

    // TODO 1: criar follower_ = std::make_shared<rclcpp::AsyncParametersClient>(this,
    //   "cylinder_follower"), o cliente dos serviços de parâmetros do nó cylinder_follower.

    // TODO 2: assinar "/pid/angular" e "/pid/linear" (Float64MultiArray, fila 10). Em cada
    //   mensagem, data = [erro, P, I, D, saída]: guarde o erro e quando ele chegou, por exemplo
    //   erro_ang_ = {m->data[0], agora()};  (o mesmo para erro_lin_).

    timer_ = rclcpp::create_timer(this, get_clock(), 100ms, [this]() { passo(); });
  }

private:
  using Amostra = std::pair<double, double>;   // (erro, instante)

  double agora() { return now().seconds(); }
  double par(const std::string & nome) const { return get_parameter(nome).as_double(); }
  std::vector<std::string> sequencia() const { return get_parameter("sequencia").as_string_array(); }

  void ir_para(const std::string & cor) {
    // TODO 3: mudar dois parâmetros do follower: "cor" para a cor pedida e "w_busca" para o
    //   parâmetro w_busca deste nó (o follower começa com 0.0, parado):
    //   follower_->set_parameters({rclcpp::Parameter("cor", cor),
    //                              rclcpp::Parameter("w_busca", par("w_busca"))});
    //   (é assíncrono: devolve um future, que aqui não precisamos esperar)
    RCLCPP_INFO(get_logger(), "indo para o cilindro %s (%d de %zu)", cor.c_str(), indice_ + 1,
                sequencia().size());
  }

  // true quando o robô está parado na frente do alvo há tempo_estavel segundos
  bool chegou() {
    const double t = agora();
    // Nos primeiros 2 s depois de trocar de cor, o follower ainda pode estar usando a detecção
    // da cor anterior (ela só vence depois do 'timeout' dele): não vale chegar.
    if (t - t_inicio_ < 2.0) {
      t_dentro_.reset();
      return false;
    }
    // TODO 4: o robô chegou se os dois erros
    //   - são recentes (chegaram há menos de 0.3 s: o follower só publica quando vê o alvo), e
    //   - estão dentro da tolerância (|erro_ang| < tol_ang e |erro_lin| < tol_lin)
    //   sem interrupção há pelo menos tempo_estavel segundos. Use t_dentro_ para marcar quando
    //   a condição começou a valer (vazio, com reset(), quando não vale).
    return false;
  }

  void proximo() {
    ++indice_;
    const auto seq = sequencia();
    if (indice_ < static_cast<int>(seq.size())) {
      estado_ = "indo";
      t_inicio_ = agora();
      t_dentro_.reset();
      ir_para(seq[indice_]);
      return;
    }
    // TODO 5: acabou a sequência. Pare o robô: mude no follower "w_busca" para 0.0 e "cor" para
    //   "nenhuma" (sem alvo e sem giro de busca, ele publica velocidade zero), passe estado_ para
    //   "fim" e escreva no log "missão concluída: salve o mapa com o map_saver_cli".
  }

  void passo() {
    if (estado_ == "esperando") {
      if (follower_ && follower_->service_is_ready()) {
        proximo();
      } else {
        RCLCPP_INFO_THROTTLE(get_logger(), *get_clock(), 5000, "esperando o cylinder_follower...");
      }
    } else if (estado_ == "indo") {
      if (chegou()) {
        RCLCPP_INFO(get_logger(), "cheguei ao %s", sequencia()[indice_].c_str());
        estado_ = "pausa";
        t_pausa_ = agora();
      // TODO 6 (extensão): se passar de tempo_max segundos sem chegar, avise no log
      //   (RCLCPP_WARN) e pule para o próximo cilindro com proximo().
      }
    } else if (estado_ == "pausa") {
      if (agora() - t_pausa_ >= par("pausa")) proximo();
    }
  }

  rclcpp::AsyncParametersClient::SharedPtr follower_;
  rclcpp::Subscription<Float64MultiArray>::SharedPtr ang_sub_, lin_sub_;
  rclcpp::TimerBase::SharedPtr timer_;
  int indice_ = -1;                       // posição na sequência (-1: ainda não começou)
  std::string estado_ = "esperando";      // esperando, indo, pausa, fim
  double t_inicio_ = 0.0, t_pausa_ = 0.0;
  std::optional<double> t_dentro_;        // desde quando os erros estão dentro da tolerância
  std::optional<Amostra> erro_ang_, erro_lin_;   // (erro, instante) mais recente de cada PID
};

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Missao>());
  rclcpp::shutdown();
  return 0;
}
