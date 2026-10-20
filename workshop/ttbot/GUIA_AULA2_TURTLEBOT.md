# Aula 2: Gazebo e TurtleBot3

Guia do instrutor. Aula de 30 min, ROS 2 Humble, C++. A turma vê você escrever, ao vivo, um nó que lê o laser do TurtleBot3 (`/scan`) e publica velocidade (`/cmd_vel`) para ele andar pelo Gazebo sem bater em nada.

Pressupõe a aula 1 ([GUIA_AULA1_DOCKER_TURTLESIM.md](GUIA_AULA1_DOCKER_TURTLESIM.md)). A turma já sabe entrar no container, já viu nós, tópicos, serviços e parâmetros no turtlesim, e já conhece o padrão dos 3 TODOs. Os passos 3 e 4 podem ir mais rápido.

Testado em ROS 2 Humble + Gazebo 11: em 2 min o robô percorre cerca de 13 m pelo `turtlebot3_world` e nunca chega a menos de 0,27 m de nada.

## Resumo

- **Duração:** 30 min, em 12 passos.
- **Conceitos:** nó, tópico, publisher, subscriber, mensagem, parâmetro, launch, ferramentas `ros2` de terminal, `rqt_graph`.
- **Terminais:** 3, todos dentro do container.
    - **T1** roda o Gazebo.
    - **T2** compila e roda o nó.
    - **T3** serve para espiar o sistema (`ros2 topic`, `ros2 param`, `rqt_graph`).
- **Código ao vivo:** cerca de 15 linhas, todas em `src/desviador.cpp`. O resto do arquivo já vem pronto.

| Trecho | Passo | Onde no arquivo | Linhas | Tempo digitando |
|---|---|---|---|---|
| TODO 1: publisher e subscriber | 6 | Construtor | 4 | ~2 min |
| TODO 2: decidir a velocidade | 7 | `scan_callback` | 8 | ~3 min |
| TODO 3: parâmetros | 9 | Construtor + `scan_callback` | 3 novas + 3 trocas | ~3 min |

## Arquivos do pacote

| Arquivo | Para quê |
|---|---|
| `src/desviador.cpp` | Exercício com os 3 TODOs. É o arquivo que você completa ao vivo |
| `src/desviador_solucao.cpp` | Versão pronta. Mostra o resultado no passo 1 e salva a aula se o seu código der erro |
| `src/desviador_turtlesim_solucao.cpp` | Plano B: o desviador da aula 1, pronto, no turtlesim |
| `launch/desviador.launch.py` | Abre Gazebo + TurtleBot3 + RViz + desviador. `rviz:=false` deixa só o Gazebo |
| `launch/turtlesim.launch.py` | Abre turtlesim + desviador da aula 1 (plano B) |

Todos os executáveis do pacote sobem com o nome de nó `/desviador`, então os comandos de parâmetro são os mesmos em todos.

## Antes da aula

- [ ] **Reconstruir a imagem** depois de puxar estas mudanças: `docker compose build` em `docker/`. Uma imagem antiga ainda tem o `ttbot` em Python e não tem o cache de modelos do Gazebo.
- [ ] **Conferir os dois problemas do compose**, já resolvidos na aula 1. Eles travam o container, e o Gazebo é mais exigente que o turtlesim:
    - **X11:** o compose monta `/tmp/.docker.xauth`, que não existe por padrão. Com Docker, sem ele o Gazebo e o rqt não abrem. No podman sem root, as janelas já abrem sem esse arquivo. No host, antes do `docker compose up` (e de novo depois de cada reboot):
      ```bash
      touch /tmp/.docker.xauth
      xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f /tmp/.docker.xauth nmerge -
      ```
      Se o Docker já criou isso como pasta, apague com `sudo rm -rf /tmp/.docker.xauth` e repita.
    - **GPU:** no Docker, `gpus: all` exige placa NVIDIA e NVIDIA Container Toolkit. Sem isso o container não sobe. Quem não tiver comenta `gpus: all` e as duas linhas `NVIDIA_*` do compose. O Gazebo roda na GPU integrada, mais devagar. O podman-compose ignora essa linha.
- [ ] **Abrir o Gazebo uma vez** em cada máquina: `ros2 launch ttbot desviador.launch.py no:=desviador_solucao`. O robô deve aparecer em poucos segundos.
- [ ] **Testar o plano B:** `ros2 launch ttbot turtlesim.launch.py no:=desviador_turtlesim_solucao`.
- [ ] **Ensaiar a aula inteira uma vez, cronometrando.** Depois do ensaio, volte o exercício ao estado original: `git checkout workshop/ttbot/src/desviador.cpp`.

### 10 minutos antes de começar

1. No host: `cd docker && docker compose up -d`.
2. Abra os 3 terminais, cada um com `docker exec -it ros_workshop bash`.
3. No T2, compile uma vez para o primeiro build ao vivo ser rápido:
   ```bash
   cd ~/workshop_ws && colcon build --packages-select ttbot && source install/setup.bash
   ```
4. No VS Code, abra `workshop/ttbot/src/desviador.cpp` e aumente a fonte (Ctrl + =).
5. Deixe este guia aberto no celular ou em outra tela.

## Roteiro

| Passo | Tempo | O que acontece | Você digita código? |
|---|---|---|---|
| 1 | 0–3 | Mostrar o resultado final | Não |
| 2 | 3–4 | Subir o robô sem o nosso nó | Não |
| 3 | 4–8 | Explorar nós, tópicos e mensagens pelo terminal | Não |
| 4 | 8–10 | Mover o robô na mão | Não |
| 5 | 10–12 | Tour pelo `desviador.cpp` | Não |
| 6 | 12–14 | TODO 1: publisher e subscriber | Sim, 4 linhas |
| 7 | 14–18 | TODO 2: a decisão, compilar e rodar | Sim, 8 linhas |
| 8 | 18–20 | Ver o nó trabalhando | Não |
| 9 | 20–25 | TODO 3: parâmetros e `ros2 param set` | Sim, 3 linhas + 3 trocas |
| 10 | 25–27 | `rqt_graph` | Não |
| 11 | 27–28 | Launch file | Não |
| 12 | 28–30 | Fechamento | Não |

**Se estiver atrasado:** pule o passo 8, o `--ros-args` do passo 9 e a leitura do launch no passo 11. **Se sobrar tempo:** faça o desafio 1 ao vivo.

---

### Passo 1: mostrar o resultado (0–3 min)

**Objetivo:** a turma ver aonde vai chegar.

**Rode:**
```bash
# T1
ros2 launch ttbot desviador.launch.py no:=desviador_solucao
```

**Fale:**
> "Esse robô está andando sozinho e desviando das paredes e dos pilares. Quem decide para onde ele vai é um programa de umas 15 linhas que a gente vai escrever agora, em C++."

Deixe rodar uns 30 s. Dê **Ctrl+C no T1**.

---

### Passo 2: subir o robô sem o nosso nó (3–4 min)

**Objetivo:** mostrar o robô "sem cérebro", parado.

**Rode:**
```bash
# T1
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

**Fale:**
> "Agora é o mesmo robô, só que sem o nosso programa. Ele tem laser e rodas, mas ninguém está mandando nada. Vamos ver o que ele oferece."

Deixe o T1 assim até o passo 11.

---

### Passo 3: explorar pelo terminal (4–8 min)

**Objetivo:** mostrar que o robô é um conjunto de nós conversando por tópicos.

**Rode no T2, um por vez, e fale depois de cada um:**

```bash
ros2 node list
```
> "Cada nome aqui é um nó, um programa rodando. Tem um nó para o laser, um para as rodas, um para a IMU..."

```bash
ros2 topic list
```
> "E esses são os tópicos, os canais por onde os nós conversam. Dois interessam para a gente: `/scan` e `/cmd_vel`."

```bash
ros2 topic info /scan --verbose
```
> "O `/scan` carrega mensagens do tipo `LaserScan`. Quem publica é o nó do laser, e ninguém está assinando ainda. O nosso nó vai ser o primeiro."

```bash
ros2 interface show sensor_msgs/msg/LaserScan
```
> "Esse é o formato da mensagem. O importante é o `ranges`, uma lista de distâncias em metros, uma por ângulo. `angle_min` e `angle_increment` dizem a qual ângulo cada distância corresponde."

```bash
ros2 topic echo /scan --once
```
Role até o `ranges`.
> "Uma leitura de verdade: 360 distâncias, uma por grau. A posição 0 é a frente do robô. O `.inf` quer dizer que não tem nada no alcance."

```bash
ros2 topic hz /scan
```
Ctrl+C depois de alguns segundos.
> "Chegam 5 leituras por segundo. Então o nosso nó vai tomar 5 decisões por segundo."

```bash
ros2 interface show geometry_msgs/msg/Twist
```
> "Esse é o formato do comando de velocidade: uma parte linear e uma angular, cada uma com x, y e z. Um robô de duas rodas só usa duas: `linear.x`, para frente, e `angular.z`, girar."

---

### Passo 4: mover o robô na mão (8–10 min)

**Objetivo:** mostrar que publicar em `/cmd_vel` move o robô. E que o Gazebo repete o último comando.

**Rode:**
```bash
# T2
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist "{angular: {z: 0.5}}"
```

**Fale:**
> "Agora eu sou o nó: estou publicando 10 vezes por segundo 'gira a 0,5 radianos por segundo'."

Dê **Ctrl+C no T2**. O robô **continua girando**.

> "Parei de publicar e ele continua girando. Na aula 1, a tartaruga parava sozinha depois de 1 s. O Gazebo não: repete o último comando para sempre. Num robô real isso é perigoso, então o nosso nó vai mandar velocidade zero quando for fechado."

**Rode:**
```bash
# T2
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{}"
```

> "Mensagem vazia é tudo zero, e o robô para. Resumindo: para controlar o robô, basta ler `/scan` e escrever em `/cmd_vel`. É exatamente isso que o nosso programa vai fazer, sozinho."

---

### Passo 5: tour pelo código (10–12 min)

**Objetivo:** a turma entender o esqueleto antes de você digitar.

**Mostre** `src/desviador.cpp` no editor, de cima para baixo:

1. **Comentário do topo:** o que o nó assina e o que publica.
2. **`#include`s:** um por tipo de mensagem que vamos usar, mais o `rclcpp`, que é a biblioteca do ROS 2 para C++.
3. **`class Desviador : public rclcpp::Node`:** todo nó é uma classe que herda de `Node`.
4. **Construtor:** é onde o nó se prepara. Mostre os dois TODOs vazios e o trecho `add_pre_shutdown_callback`, que manda velocidade zero no Ctrl+C (o problema do passo 4).
5. **`scan_callback`:** é chamada sozinha a cada leitura nova do laser, 5 vezes por segundo. Mostre o TODO 2.
6. **`distancia_frente`:** já vem pronta. Devolve a menor distância num cone de ±30° à frente.
7. **Constantes `DISTANCIA`, `VELOCIDADE`, `VELOCIDADE_GIRO`:** os valores que vamos usar por enquanto.
8. **`main`:** inicia o ROS, cria o nó e fica em `spin`, esperando mensagens.

**Fale:**
> "A função `distancia_frente` é só geometria, não tem nada de ROS, então já deixei pronta. A gente vai escrever a parte de ROS: conectar nos tópicos e decidir o que fazer com cada leitura."

---

### Passo 6: TODO 1, publisher e subscriber (12–14 min)

**Objetivo:** conectar o nó aos dois tópicos.

**Digite** no construtor, no lugar do comentário `TODO 1`:

```cpp
pub_ = create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);
sub_ = create_subscription<sensor_msgs::msg::LaserScan>(
  "scan", 10,
  std::bind(&Desviador::scan_callback, this, std::placeholders::_1));
```

**Fale, enquanto digita:**
> "Primeira linha: vou **publicar** mensagens `Twist` no tópico `cmd_vel`. O tipo vai entre os sinais de menor e maior. O 10 é o tamanho da fila."

> "Segunda: vou **assinar** mensagens `LaserScan` do tópico `scan`. E o `std::bind` diz: quando chegar uma mensagem, chame o `scan_callback` deste objeto, passando a mensagem no lugar do `_1`."

> "Os nomes vão sem barra, `scan` e não `/scan`. Assim o mesmo código serve para vários robôs, cada um no seu namespace."

Ainda não compile: falta a decisão.

---

### Passo 7: TODO 2, decidir, compilar e rodar (14–18 min)

**Objetivo:** o robô andar sozinho.

**Digite** em `scan_callback`, no lugar do comentário `TODO 2`:

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

**Fale, enquanto digita:**
> "Primeiro, qual a distância até a coisa mais próxima à frente."

> "Crio um comando. O `Twist` nasce todo zerado, então só preencho o que me interessa."

> "Obstáculo a menos de meio metro? Gira no lugar. Caminho livre? Anda para frente."

> "E publico. Essa função roda 5 vezes por segundo, então o robô reavalia o tempo todo."

**Rode:**
```bash
# T2
colcon build --packages-select ttbot
source install/setup.bash
ros2 run ttbot desviador
```

O build leva cerca de 10 s. Enquanto isso:
> "O `colcon build` compila o pacote, e o `source` avisa o terminal que o pacote novo existe. Esqueceu o `source`? O `ros2 run` não acha o programa."

O robô começa a andar e desviar.
> "Pronto: é o código que a gente acabou de escrever dirigindo o robô."

**Se der errado:** erro de compilação, compare com `src/desviador_solucao.cpp`. Sem tempo para investigar, rode `ros2 run ttbot desviador_solucao` e siga a aula.

---

### Passo 8: ver o nó trabalhando (18–20 min)

**Objetivo:** mostrar o nó "por fora", com as mesmas ferramentas do passo 3.

**Rode:**
```bash
# T3
ros2 node info /desviador
```
> "Agora o nosso nó aparece no sistema: assina `/scan` e publica `/cmd_vel`. Os outros tópicos, como `/rosout` e `/parameter_events`, todo nó ganha de brinde."

```bash
# T3
ros2 topic echo /cmd_vel
```
> "Esses são os comandos que o nosso nó está mandando. Quando o robô chega perto de algo, o `linear.x` vira zero e o `angular.z` vira 0,8."

Ctrl+C no T3.

---

### Passo 9: TODO 3, parâmetros (20–25 min)

**Objetivo:** mudar o comportamento sem recompilar.

**Fale:**
> "E se eu quiser que ele desvie mais cedo? Do jeito que está, tenho que mudar a constante e recompilar. Para isso existem os parâmetros."

**Digite** no construtor, no lugar do comentário `TODO 3`:

```cpp
declare_parameter("distancia", 0.5);        // m
declare_parameter("velocidade", 0.15);      // m/s
declare_parameter("velocidade_giro", 0.8);  // rad/s
```

**Troque**, dentro do `scan_callback`:

| Antes | Depois |
|---|---|
| `DISTANCIA` | `get_parameter("distancia").as_double()` |
| `VELOCIDADE_GIRO` | `get_parameter("velocidade_giro").as_double()` |
| `VELOCIDADE` | `get_parameter("velocidade").as_double()` |

**Fale:**
> "`declare_parameter` cria o parâmetro com um valor padrão. E como eu leio o valor a cada mensagem, se alguém mudar, vale na hora."

Dê **Ctrl+C no T2**. O robô para.
> "Lembram do passo 4? Agora o robô parou, porque o nó mandou velocidade zero antes de fechar."

**Rode:**
```bash
# T2
colcon build --packages-select ttbot && source install/setup.bash
ros2 run ttbot desviador
```

```bash
# T3
ros2 param list /desviador
ros2 param get /desviador distancia
ros2 param set /desviador distancia 1.0
```
> "Agora ele desvia a um metro, bem antes. Não recompilei nem reiniciei nada."

```bash
# T3
ros2 param set /desviador velocidade 0.22
```
> "0,22 m/s é a velocidade máxima desse robô."

**Opcional, se der tempo.** Ctrl+C no T2 e:
```bash
# T2
ros2 run ttbot desviador --ros-args -p distancia:=0.3
```
> "Também dá para escolher o valor na hora de iniciar."

---

### Passo 10: o grafo (25–27 min)

**Objetivo:** ver o sistema inteiro num desenho.

**Rode:**
```bash
# T3
rqt_graph
```
Se aparecer vazio, clique no botão de atualizar (canto superior esquerdo).

**Mostre** o caminho com o mouse: nó do laser → `/scan` → `/desviador` → `/cmd_vel` → nó das rodas.

**Fale:**
> "É o mesmo que vimos no terminal, só que desenhado. Sensor de um lado, atuador do outro, e o nosso nó no meio, decidindo. Quase todo robô é assim, só que com mais caixinhas."

Feche o `rqt_graph`.

---

### Passo 11: launch file (27–28 min)

**Objetivo:** subir tudo com um comando só.

Dê **Ctrl+C no T2** (o nó) e **no T1** (o Gazebo).

**Fale:**
> "Até agora foram dois terminais: um para o Gazebo e outro para o nosso nó. No dia a dia, a gente usa um launch file."

**Rode:**
```bash
# T1
ros2 launch ttbot desviador.launch.py
```
> "Esse sobe o mundo, o robô, o RViz e o nosso nó, com o código que vocês acabaram de ver escrito."

> "O Gazebo é a simulação: o mundo de mentira, com física. O RViz só desenha o que o robô está percebendo. Os pontinhos em volta dele são as 360 distâncias do `/scan`."

**Mostre** `launch/desviador.launch.py`, em três partes:
1. `DeclareLaunchArgument`: um argumento para escolher qual executável rodar e outro para ligar ou desligar o RViz.
2. `IncludeLaunchDescription`: reaproveita o launch do TurtleBot3.
3. `Node`: o RViz, que só abre se `rviz` for `true`, e o nosso nó, com os parâmetros.

> "O launch é em Python porque o ROS 2 não tem launch em C++, só em Python, XML ou YAML. Mas ele não é código do robô: só diz quais nós subir e com quais parâmetros."

---

### Passo 12: fechamento (28–30 min)

**Fale:**
> "Recapitulando em uma frase cada:
> **nó** é um programa;
> **tópico** é o canal por onde os nós conversam, uns publicando, outros assinando;
> **mensagem** é o formato do que passa no tópico;
> **parâmetro** é uma configuração que muda sem recompilar;
> **launch** sobe tudo de uma vez."

> "Para casa, tem quatro desafios no guia. O primeiro é fazer o robô girar para o lado mais livre, em vez de sempre para a esquerda."

Passe os [desafios](#desafios-para-casa) e abra para perguntas.

---

## Plano B: turtlesim

Use se o Gazebo não abrir na máquina do projetor. O turtlesim roda em qualquer lugar, sem GPU. A turma já conhece ele da aula 1, então dá para ir rápido. A estrutura da aula é a mesma, mas no passo 6–9 você **lê** o código pronto com a turma, em vez de digitar.

| Passo | O que muda |
|---|---|
| 1 | `ros2 launch ttbot turtlesim.launch.py no:=desviador_turtlesim_solucao` (T1). Ctrl+C depois de 30 s |
| 2 | `ros2 run turtlesim turtlesim_node` (T1) |
| 3 | `ros2 topic list`, `ros2 topic echo /turtle1/pose --once`, `ros2 interface show turtlesim/msg/Pose` (T2). Fale: "a tartaruga não tem laser, mas publica onde está" |
| 4 | `ros2 topic pub --rate 10 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}, angular: {z: 1.0}}"` (T2): ela anda em círculo. Ctrl+C: ela **para sozinha** depois de 1 s, ao contrário do Gazebo |
| 5–7 | Leia `src/desviador_turtlesim_solucao.cpp` com a turma. Fale: "o sensor aqui é olhar um ponto 1 m à frente e ver se ele cai fora da janela". Rode `ros2 run ttbot desviador_turtlesim_solucao` (T2) |
| 8 | `ros2 node info /desviador` e `ros2 topic echo /turtle1/cmd_vel` (T3) |
| 9 | `ros2 param set /desviador distancia 2.0` (T3) |
| 10 | `rqt_graph` (T3) |
| 11 | Ctrl+C no T1 e no T2. `ros2 launch ttbot turtlesim.launch.py no:=desviador_turtlesim_solucao` (T1) |
| 12 | Igual |

## Problemas comuns na hora

| Sintoma | O que fazer |
|---|---|
| Container não sobe: `could not select device driver "nvidia"` | Comentar `gpus: all` e as linhas `NVIDIA_*` do compose |
| `touch: cannot touch '/tmp/.docker.xauth'` ou `Is a directory` | O Docker ou o podman criou uma pasta com esse nome: `sudo rm -rf /tmp/.docker.xauth` e repetir os comandos do xauth |
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
- **Qual a diferença entre tópico, serviço e ação?** Tópico é um fluxo contínuo, sem resposta. Serviço é pergunta e resposta rápida. Exemplo ao vivo: `ros2 service call /reset_world std_srvs/srv/Empty` volta o robô ao ponto inicial. Ação é uma tarefa longa, com progresso e possibilidade de cancelar.
- **Como o código sabe onde é a frente do laser?** `distancia_frente` calcula o ângulo de cada leitura com `angle_min` e `angle_increment`, então funciona com qualquer laser, não só o do burger.

## Desafios para casa

1. Girar para o lado mais livre: comparar a distância à esquerda e à direita antes de girar.
2. Frear aos poucos: velocidade proporcional à distância do obstáculo, em vez de liga/desliga.
3. Seguir a parede a 0,4 m, usando as leituras do lado direito.
4. Ligar e desligar o robô por um serviço `std_srvs/srv/SetBool`.
