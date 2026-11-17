"""Aula 6 — controlador PID.

Um PID discreto, usado pelo cylinder_follower (um para girar, outro para andar).
Complete os TODO 1 a 4 (o 5 é extensão). Não é um nó: é só uma classe Python.
"""


class PID:
    """saida = Kp*e + Ki*integral(e) + Kd*de/dt, com limites na integral e na saída."""

    def __init__(self, kp=0.0, ki=0.0, kd=0.0, saida_max=1.0, integral_max=1.0, alfa_d=0.0):
        self.ajustar(kp, ki, kd)
        self.saida_max = saida_max          # |saída| nunca passa disto (saturação do atuador)
        self.integral_max = integral_max    # |integral do erro| nunca passa disto (anti-windup)
        self.alfa_d = alfa_d                # 0 = sem filtro na derivada; perto de 1 = filtro forte
        self.reset()

    def ajustar(self, kp, ki, kd):
        self.kp, self.ki, self.kd = kp, ki, kd

    def reset(self):
        """Esquece a história: zera a integral e a derivada (use ao perder o alvo)."""
        self.integral = 0.0
        self.erro_anterior = None
        self.derivada = 0.0
        self.p = self.i = self.d = 0.0      # últimos termos, para depurar no rqt_plot

    def update(self, erro, dt):
        """Recebe o erro atual e o tempo desde a última chamada (s); devolve a saída."""
        if dt <= 0.0:
            return 0.0

        # TODO 1: termo proporcional, self.p = Kp * erro.

        # TODO 2: termo integral. Acumule self.integral += erro * dt, limite-o a
        #   [-self.integral_max, self.integral_max] (anti-windup: sem isso, a integral cresce
        #   enquanto a saída está saturada e o robô passa muito do ponto) e faça
        #   self.i = Ki * self.integral.

        # TODO 3: termo derivativo. A derivada é (erro - self.erro_anterior) / dt; na primeira
        #   chamada (self.erro_anterior is None) use 0. Guarde self.erro_anterior = erro,
        #   ponha a derivada em self.derivada e faça self.d = Kd * self.derivada.
        # TODO 5 (extensão): a derivada amplifica o ruído da medida. Filtre-a antes de
        #   multiplicar por Kd: self.derivada = alfa_d * self.derivada + (1 - alfa_d) * bruta.

        # TODO 4: some os três termos e limite a soma a [-self.saida_max, self.saida_max].
        return 0.0
