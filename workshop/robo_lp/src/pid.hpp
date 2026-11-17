// Aula 6 — controlador PID
// Um PID discreto, usado pelo cylinder_follower (um para girar, outro para andar).
// Complete os TODO 1 a 4 (o 5 é extensão). Não é um nó: é só uma classe.
#pragma once

#include <algorithm>

// saida = Kp*e + Ki*integral(e) + Kd*de/dt, com limites na integral e na saída.
class PID {
public:
  PID(double saida_max = 1.0, double integral_max = 1.0)
  : saida_max(saida_max), integral_max(integral_max) { reset(); }

  void ajustar(double kp, double ki, double kd) { kp_ = kp; ki_ = ki; kd_ = kd; }

  // Esquece a história: zera a integral e a derivada (use ao perder o alvo).
  void reset() {
    integral_ = 0.0;
    derivada_ = 0.0;
    tem_anterior_ = false;
    p = i = d = 0.0;
  }

  // Recebe o erro atual e o tempo desde a última chamada (s); devolve a saída.
  double update(double erro, double dt) {
    if (dt <= 0.0) return 0.0;

    // TODO 1: termo proporcional, p = kp_ * erro.

    // TODO 2: termo integral. Acumule integral_ += erro * dt, limite-o a
    //   [-integral_max, integral_max] com std::clamp (anti-windup: sem isso, a integral cresce
    //   enquanto a saída está saturada e o robô passa muito do ponto) e faça i = ki_ * integral_.

    // TODO 3: termo derivativo. A derivada é (erro - erro_anterior_) / dt; na primeira chamada
    //   (tem_anterior_ falso) use 0. Guarde erro_anterior_ = erro e tem_anterior_ = true,
    //   ponha a derivada em derivada_ e faça d = kd_ * derivada_.
    // TODO 5 (extensão): a derivada amplifica o ruído da medida. Filtre-a antes de
    //   multiplicar por kd_: derivada_ = alfa_d * derivada_ + (1 - alfa_d) * bruta.

    // TODO 4: some os três termos e limite a soma a [-saida_max, saida_max].
    return 0.0;
  }

  double saida_max;      // |saída| nunca passa disto (saturação do atuador)
  double integral_max;   // |integral do erro| nunca passa disto (anti-windup)
  double alfa_d = 0.0;   // 0 = sem filtro na derivada; perto de 1 = filtro forte
  double p = 0.0, i = 0.0, d = 0.0;   // últimos termos, para depurar no rqt_plot

private:
  double kp_ = 0.0, ki_ = 0.0, kd_ = 0.0;
  double integral_ = 0.0, derivada_ = 0.0, erro_anterior_ = 0.0;
  bool tem_anterior_ = false;
};
