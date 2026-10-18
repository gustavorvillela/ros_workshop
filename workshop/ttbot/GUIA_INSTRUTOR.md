# Guia do instrutor: robô que desvia de obstáculos

Mini workshop de 30 min, ROS 2 Humble, C++. A turma escreve um nó que lê o laser do TurtleBot3 (`/scan`) e publica velocidade (`/cmd_vel`) para ele andar pelo Gazebo sem bater nas paredes.

**Conceitos cobertos:** nó, tópico, publisher, subscriber, tipo de mensagem, parâmetros, launch, ferramentas `ros2` de terminal e `rqt_graph`.

Testado em ROS 2 Humble + Gazebo 11: em 2 min o robô percorre cerca de 13 m pelo `turtlebot3_world` e nunca chega a menos de 0,27 m de nada.

## Arquivos do pacote

| Arquivo | Para quê |
|---|---|
| `src/desviador.cpp` | Exercício com 3 TODOs. É o arquivo que você completa ao vivo |
| `src/desviador_solucao.cpp` | Versão pronta. Serve para mostrar o resultado no início e socorrer quem se perder |
| `src/desviador_turtlesim.cpp` | Plano B: a mesma lógica no turtlesim, sem Gazebo |
| `launch/desviador.launch.py` | Abre Gazebo + TurtleBot3 + desviador |
| `launch/turtlesim.launch.py` | Abre turtlesim + desviador do plano B |

Os três executáveis (`desviador`, `desviador_solucao`, `desviador_turtlesim`) sobem com o nome de nó `/desviador`, então os comandos de parâmetro são os mesmos em todos.

Todos os comandos abaixo rodam **dentro do container**, a partir de `~/workshop_ws`.

## Antes da aula

- [ ] **Reconstruir a imagem** depois de puxar estas mudanças (`docker compose build` em `docker/`). Uma imagem antiga ainda tem o `ttbot` em Python e não tem o cache de modelos do Gazebo (ver abaixo). Sem reconstruir, dentro do container: `rm -rf build/ttbot install/ttbot && colcon build --packages-select ttbot`.
- [ ] **Combinar com seu amigo os dois problemas do compose**, porque eles travam o container antes da sua parte:
    - **X11:** o compose monta `/tmp/.docker.xauth`, que não existe por padrão. Sem ele, Gazebo e rqt não abrem. No host, antes do `docker compose up` (e de novo depois de cada reboot):
      ```bash
      touch /tmp/.docker.xauth
      xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f /tmp/.docker.xauth nmerge -
      ```
      Se o Docker já criou isso como pasta, apague com `sudo rm -rf /tmp/.docker.xauth` e repita. Atalho alternativo: `xhost +local:` no host.
    - **GPU:** `gpus: all` exige placa NVIDIA e NVIDIA Container Toolkit. Sem isso, o container nem sobe. Quem não tiver comenta `gpus: all` e as duas linhas `NVIDIA_*` do compose. O Gazebo roda na GPU integrada ou em software, só que mais devagar.
- [ ] **Abrir o Gazebo uma vez** em cada máquina antes da aula: `ros2 launch ttbot desviador.launch.py no:=desviador_solucao`. Sem cache, o primeiro start baixa modelos da internet e leva mais de 30 s. Aí o robô não aparece (`Spawn service failed`). O Dockerfile agora já deixa esses modelos no cache, e com isso o robô aparece em cerca de 2 s.
- [ ] **Testar o plano B:** `ros2 launch ttbot turtlesim.launch.py`.
- [ ] **Ensaiar a aula inteira uma vez, cronometrando.**
- [ ] **Na hora:** 3 terminais abertos no container e `src/desviador.cpp` aberto no editor com fonte grande.

## Roteiro de 30 minutos

| Tempo | Bloco | Conceito |
|---|---|---|
| 0–3 | Mostrar o resultado final rodando | Motivação |
| 3–10 | Explorar o robô só pelo terminal | O robô é um conjunto de nós e tópicos |
| 10–20 | Escrever o nó: TODO 1 e TODO 2 | Publisher, subscriber, callback |
| 20–25 | Parâmetros: TODO 3 e `ros2 param set` ao vivo | Parâmetros |
| 25–28 | `rqt_graph` e launch file | Grafo, launch |
| 28–30 | Fechamento e desafios | |

### 0–3 min: mostrar o resultado

```bash
ros2 launch ttbot desviador.launch.py no:=desviador_solucao
```

Deixe o robô rodar uns 30 s e diga: "em 25 minutos vocês vão escrever isso: um nó que lê o laser e decide a velocidade". Feche com Ctrl+C.

### 3–10 min: explorar o robô pelo terminal

Terminal 1, só o robô, sem o nosso nó:

```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

Terminal 2, um comando por vez, comentando cada um:

```bash
ros2 node list                                   # quem está rodando
ros2 topic list                                  # por onde eles conversam
ros2 topic info /scan --verbose                  # tipo, quem publica e quem assina
ros2 interface show sensor_msgs/msg/LaserScan    # o formato da mensagem do laser
ros2 topic hz /scan                              # quantas leituras por segundo (~5)
ros2 topic echo /scan --once                     # uma leitura de verdade (ranges = distâncias em m)
ros2 interface show geometry_msgs/msg/Twist      # o formato do comando de velocidade
```

Agora mova o robô na mão:

```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist "{angular: {z: 0.5}}"
```

Dê Ctrl+C e mostre que **o robô continua girando**: o Gazebo mantém o último comando que recebeu. Pare com:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{}"
```

Fale: "pra controlar o robô, basta ler `/scan` e escrever em `/cmd_vel`. É isso que o nosso nó vai fazer sozinho." Deixe o Gazebo aberto no terminal 1.

### 10–20 min: escrever o nó (TODO 1 e 2)

Abra `src/desviador.cpp` e mostre a estrutura antes de digitar:

- a classe herda de `rclcpp::Node`, e o construtor é onde o nó se prepara;
- `scan_callback` é chamada a cada leitura nova do laser;
- `distancia_frente` já está pronta e devolve a menor distância num cone de ±30° à frente. Diga que é só geometria, não ROS;
- `main` inicia o ROS, cria o nó e fica em `spin`, esperando mensagens.

Digite o TODO 1 e o TODO 2 (código na seção [Cola do live coding](#cola-do-live-coding)). Depois, no terminal 2:

```bash
cd ~/workshop_ws
colcon build --packages-select ttbot
source install/setup.bash
ros2 run ttbot desviador
```

O robô começa a andar e a desviar. Se algo der errado, `ros2 run ttbot desviador_solucao` resolve na hora.

### 20–25 min: parâmetros (TODO 3)

Pergunte: "e se eu quiser outra distância? Recompilo?". Digite o TODO 3, recompile e rode de novo. No terminal 3:

```bash
ros2 param list /desviador
ros2 param get /desviador distancia
ros2 param set /desviador distancia 1.0      # passa a desviar bem antes
ros2 param set /desviador velocidade 0.22    # 0.22 m/s é a velocidade máxima do burger
```

Mostre também que dá para passar o valor na hora de iniciar:

```bash
ros2 run ttbot desviador --ros-args -p distancia:=0.3
```

### 25–28 min: grafo e launch

Com o nó rodando:

```bash
rqt_graph
```

Aponte o caminho `/scan` → `/desviador` → `/cmd_vel` → Gazebo.

Feche tudo e mostre que um launch file sobe o mundo, o robô e o nó com um comando só:

```bash
ros2 launch ttbot desviador.launch.py
```

Abra `launch/desviador.launch.py` e mostre o `IncludeLaunchDescription` (reaproveita o launch do TurtleBot3) e o `Node` com os parâmetros.

### 28–30 min: fechamento

Recapitule em uma frase cada: nó, tópico (pub/sub), mensagem, parâmetro, launch. Passe os [desafios](#desafios-para-casa).

## Cola do live coding

**TODO 1**, no construtor:

```cpp
pub_ = create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);
sub_ = create_subscription<sensor_msgs::msg::LaserScan>(
  "scan", 10,
  std::bind(&Desviador::scan_callback, this, std::placeholders::_1));
```

- `create_publisher<Tipo>("tópico", 10)`: o tipo da mensagem vai entre `< >`. O 10 é o tamanho da fila de mensagens.
- O nome vai sem a barra (`"scan"`, não `"/scan"`). Assim o nó também funciona dentro de um namespace, por exemplo com dois robôs.
- `std::bind(...)`: diz "quando chegar mensagem, chame `scan_callback` deste objeto". O `_1` marca o lugar da mensagem.

**TODO 2**, em `scan_callback`:

```cpp
const double dist = distancia_frente(*msg, CONE_GRAUS);

geometry_msgs::msg::Twist cmd;
if (dist < DISTANCIA) {
  cmd.angular.z = VELOCIDADE_GIRO;  // obstáculo: gira no lugar
} else {
  cmd.linear.x = VELOCIDADE;        // livre: anda para frente
}
pub_->publish(cmd);
```

- `Twist` começa zerado. Só preenchemos o campo que interessa.
- `linear.x` é para frente (m/s) e `angular.z` é girar no próprio eixo (rad/s, positivo = anti-horário).

**TODO 3**, no construtor:

```cpp
declare_parameter("distancia", 0.5);        // m
declare_parameter("velocidade", 0.15);      // m/s
declare_parameter("velocidade_giro", 0.8);  // rad/s
```

E no `scan_callback`, troque as constantes:

| Antes | Depois |
|---|---|
| `DISTANCIA` | `get_parameter("distancia").as_double()` |
| `VELOCIDADE_GIRO` | `get_parameter("velocidade_giro").as_double()` |
| `VELOCIDADE` | `get_parameter("velocidade").as_double()` |

O parâmetro é lido a cada mensagem, por isso o `ros2 param set` vale na hora. As constantes do fim da classe podem ser apagadas.

## Plano B: turtlesim

Use se o Gazebo não abrir na máquina do projetor ou na maioria das máquinas da turma. O turtlesim roda em qualquer lugar, sem GPU.

```bash
ros2 launch ttbot turtlesim.launch.py
```

Os blocos da aula continuam os mesmos, com estas trocas:

| Bloco | No Gazebo | No turtlesim |
|---|---|---|
| Explorar | `/scan` e `/cmd_vel` | `/turtle1/pose` e `/turtle1/cmd_vel` (rode só `ros2 run turtlesim turtlesim_node`) |
| Mover na mão | `ros2 topic pub ... /cmd_vel ...` | `ros2 topic pub ... /turtle1/cmd_vel ...`. A tartaruga **para sozinha** 1 s depois do último comando, ao contrário do Gazebo |
| Escrever o nó | Live coding dos TODOs | Leia `src/desviador_turtlesim.cpp` com a turma. O "sensor" é olhar um ponto à frente e ver se ele cai fora da janela |
| Parâmetros | `ros2 param set /desviador ...` | Os mesmos comandos. Ex.: `ros2 param set /desviador distancia 2.0` |

## Problemas comuns na hora

| Sintoma | O que fazer |
|---|---|
| Container não sobe: `could not select device driver "nvidia"` | Comentar `gpus: all` e as linhas `NVIDIA_*` do compose |
| Podman: `statfs /tmp/.docker.xauth: no such file or directory` | O podman não cria o arquivo sozinho. Rodar os dois comandos do xauth em [Antes da aula](#antes-da-aula) |
| Podman: build falha com `source: not found` | O podman ignora o `SHELL` do Dockerfile. Já corrigido no Dockerfile (usa `. setup.sh`); puxar a versão nova |
| Podman: Gazebo não usa a placa NVIDIA | O podman-compose ignora `gpus: all`. O Gazebo roda na GPU integrada pelo `/dev/dri`, e isso basta para a aula |
| Gazebo/rqt não abre: `cannot open display` ou `Authorization required` | Refazer o `/tmp/.docker.xauth` no host, ou rodar `xhost +local:` (ver [Antes da aula](#antes-da-aula)) |
| Gazebo abre mas o robô não aparece: `Spawn service failed` | Primeiro start sem cache de modelos. Feche e rode o launch de novo (da segunda vez é rápido) ou reconstrua a imagem |
| Launch do TurtleBot3 falha com `KeyError: 'TURTLEBOT3_MODEL'` | `export TURTLEBOT3_MODEL=burger`. O launch do `ttbot` e o compose já definem isso |
| Monte de `ALSA lib ... error` no terminal do Gazebo | Ignorar: é só o container sem placa de som |
| `ros2 topic list` (ou outro `ros2`) dá `RuntimeError: !rclpy.ok()` | Daemon do ROS travado: `ros2 daemon stop` e tentar de novo |
| `Package 'ttbot' not found` ou `No executable found` | Esqueceu de rodar `source install/setup.bash` depois do build |
| Erro de build com resto do `ttbot` antigo em Python | `rm -rf build/ttbot install/ttbot` e compilar de novo |
| Nó roda mas o robô não se mexe | Conferir o TODO 1 (nomes `"scan"` e `"cmd_vel"`) e se `ros2 topic echo /cmd_vel` mostra mensagens |
| Robô continua andando depois de fechar um `ros2 topic pub` | `ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{}"` |
| Robô bateu, tombou ou ficou preso | `ros2 service call /reset_world std_srvs/srv/Empty` volta o robô ao início. No Gazebo: Edit → Reset Model Poses |
| Gazebo muito lento | Máquina sem GPU. Siga a aula pelo projetor ou use o plano B |

## Perguntas prováveis

- **Por que o robô não para quando o nó morre?** O plugin de rodas do Gazebo repete o último comando para sempre. Robôs reais têm um *watchdog* que zera a velocidade se os comandos param de chegar. Por isso o nó manda velocidade zero ao receber Ctrl+C (o trecho com `add_pre_shutdown_callback`).
- **O que é esse 10 no publisher e no subscriber?** É a QoS mais simples: guardar até 10 mensagens na fila. QoS são as regras de entrega de um tópico. Muitos drivers de sensor usam *best effort*, que não reenvia o que se perdeu. Nesses casos o subscriber precisa de `rclcpp::SensorDataQoS()`. O laser do Gazebo usa *reliable*, então o 10 basta.
- **Por que `std::bind` e não uma lambda?** Os dois funcionam. O `std::bind` é o que aparece nos tutoriais oficiais do ROS 2.
- **C++ ou Python?** As APIs são quase iguais (`rclcpp` e `rclpy`). C++ é o padrão quando importa desempenho ou tempo de resposta. Python é mais rápido de escrever.
- **Por que o launch é em Python, se a aula é em C++?** O ROS 2 não tem launch em C++, só em Python, XML ou YAML. O launch não é código do robô: só diz quais nós subir e com quais parâmetros.
- **Qual a diferença entre tópico, serviço e ação?** Tópico é um fluxo contínuo, sem resposta. Serviço é pergunta e resposta rápida. Exemplo ao vivo: `ros2 service call /reset_world std_srvs/srv/Empty` volta o robô ao ponto inicial. Ação é uma tarefa longa, com progresso e possibilidade de cancelar.
- **Como o código sabe onde é a frente do laser?** `distancia_frente` calcula o ângulo de cada leitura com `angle_min` e `angle_increment`, então funciona com qualquer laser, não só o do burger.

## Desafios para casa

1. Girar para o lado mais livre: comparar a distância à esquerda e à direita antes de girar.
2. Frear aos poucos: velocidade proporcional à distância do obstáculo, em vez de liga/desliga.
3. Seguir a parede a 0,4 m, usando as leituras do lado direito.
4. Ligar e desligar o robô por um serviço `std_srvs/srv/SetBool`.
