"""Aula 7 — missao.

Usa os cilindros como waypoints: manda o cylinder_follower (Aula 6) até cada cor da
'sequencia', espera ele chegar, faz uma pausa e passa para a próxima. No fim, para o
robô. Enquanto isso o Cartographer (Aula 3) faz o mapa.

O nó não comanda as rodas: ele só muda o parâmetro 'cor' do cylinder_follower, por
meio do serviço de parâmetros dele, e acompanha os erros que o follower publica em
/pid/angular e /pid/linear para saber quando o robô chegou.

Complete os TODO 1 a 5 (o 6 é extensão).
Rode com: ros2 run robo_py missao --ros-args -p use_sim_time:=true
"""
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.parameter_client import AsyncParameterClient
from std_msgs.msg import Float64MultiArray


class Missao(Node):

    def __init__(self):
        super().__init__('missao')
        self.declare_parameter('sequencia', ['verde', 'azul', 'amarelo', 'vermelho'])
        self.declare_parameter('tol_lin', 0.10)          # m: erro de distância aceito na chegada
        self.declare_parameter('tol_ang', 0.05)          # rad: erro angular aceito na chegada
        self.declare_parameter('tempo_estavel', 1.0)     # s dentro da tolerância para valer
        self.declare_parameter('pausa', 2.0)             # s parado em cada cilindro
        self.declare_parameter('tempo_max', 180.0)       # s por cilindro (TODO 6)
        self.declare_parameter('w_busca', 0.3)           # rad/s: giro de busca do follower

        self.indice = -1            # posição na sequência (-1: ainda não começou)
        self.estado = 'esperando'   # esperando, indo, pausa, fim
        self.t_inicio = None        # quando começou a ir para o cilindro atual
        self.t_dentro = None        # desde quando os erros estão dentro da tolerância
        self.t_pausa = None
        self.erro_ang = None        # (erro, instante) mais recente de cada PID
        self.erro_lin = None

        # TODO 1: criar self.follower = AsyncParameterClient(self, 'cylinder_follower'), o
        #   cliente dos serviços de parâmetros do nó cylinder_follower.
        self.follower = None

        # TODO 2: assinar '/pid/angular' e '/pid/linear' (Float64MultiArray, fila 10),
        #   chamando self.on_ang e self.on_lin.

        self.create_timer(0.1, self.passo)

    def agora(self):
        return self.get_clock().now().nanoseconds * 1e-9

    # data = [erro, P, I, D, saída]: guardamos o erro e quando ele chegou
    def on_ang(self, msg):
        self.erro_ang = (msg.data[0], self.agora())

    def on_lin(self, msg):
        self.erro_lin = (msg.data[0], self.agora())

    def ir_para(self, cor):
        # TODO 3: mudar dois parâmetros do follower: 'cor' para a cor pedida e 'w_busca' para o
        #   parâmetro w_busca deste nó (o follower começa com 0.0, parado):
        #   self.follower.set_parameters([Parameter('cor', value=cor),
        #                                 Parameter('w_busca', value=w_busca)])
        #   (é assíncrono: devolve um Future, que aqui não precisamos esperar)
        self.get_logger().info(f'indo para o cilindro {cor} '
                               f'({self.indice + 1} de {len(self.sequencia())})')

    def sequencia(self):
        return list(self.get_parameter('sequencia').value)

    def chegou(self):
        """True quando o robô está parado na frente do alvo há tempo_estavel segundos."""
        t = self.agora()
        p = lambda nome: self.get_parameter(nome).value
        # Nos primeiros 2 s depois de trocar de cor, o follower ainda pode estar usando a
        # detecção da cor anterior (ela só vence depois do 'timeout' dele): não vale chegar.
        if t - self.t_inicio < 2.0:
            self.t_dentro = None
            return False
        # TODO 4: o robô chegou se os dois erros
        #   - são recentes (chegaram há menos de 0.3 s: o follower só publica quando vê o alvo), e
        #   - estão dentro da tolerância (|erro_ang| < tol_ang e |erro_lin| < tol_lin)
        #   sem interrupção há pelo menos tempo_estavel segundos. Use self.t_dentro para marcar
        #   quando a condição começou a valer (None quando não vale).
        return False

    def proximo(self):
        self.indice += 1
        seq = self.sequencia()
        if self.indice < len(seq):
            self.estado = 'indo'
            self.t_inicio = self.agora()
            self.t_dentro = None
            self.ir_para(seq[self.indice])
            return
        # TODO 5: acabou a sequência. Pare o robô: mude no follower 'w_busca' para 0.0 e 'cor'
        #   para 'nenhuma' (sem alvo e sem giro de busca, ele publica velocidade zero), passe
        #   self.estado para 'fim' e escreva no log 'missão concluída: salve o mapa com o
        #   map_saver_cli'.

    def passo(self):
        if self.estado == 'esperando':
            if self.follower is not None and self.follower.services_are_ready():
                self.proximo()
            else:
                self.get_logger().info('esperando o cylinder_follower...', throttle_duration_sec=5.0)
        elif self.estado == 'indo':
            if self.chegou():
                self.get_logger().info(f'cheguei ao {self.sequencia()[self.indice]}')
                self.estado = 'pausa'
                self.t_pausa = self.agora()
            # TODO 6 (extensão): se passar de tempo_max segundos sem chegar, avise no log
            #   (get_logger().warn) e pule para o próximo cilindro com self.proximo().
        elif self.estado == 'pausa':
            if self.agora() - self.t_pausa >= self.get_parameter('pausa').value:
                self.proximo()


def main(args=None):
    rclpy.init(args=args)
    node = Missao()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
