# Aula 1: Docker e conceitos básicos de ROS 2 com turtlesim

Guia do instrutor. Aula de 30 min, ROS 2 Humble, C++. A turma aprende a entrar no ambiente pelo Docker e vê, **na tela**, os conceitos básicos do ROS 2: nós, tópicos, mensagens, serviços e parâmetros. No fim, você escreve ao vivo um nó que faz a tartaruga andar sozinha sem bater nas paredes.

A aula 2 ([GUIA_AULA2_TURTLEBOT.md](GUIA_AULA2_TURTLEBOT.md)) repete o mesmo padrão de código num robô com laser, no Gazebo.

Testado na imagem do workshop: em 60 s a tartaruga percorre a janela inteira e não bate nenhuma vez na parede.

## Resumo

- **Duração:** 30 min, em 12 passos. Sem cortes, pode chegar a 35.
- **Terminais:**
    - **H**, no host, só para os comandos `docker`.
    - **T1**, no container, roda o turtlesim.
    - **T2**, no container, roda o teclado, os comandos `ros2` e o nosso nó.
    - **T3**, no container, abre as janelas gráficas. Elas sempre levam `&` no fim, para o terminal continuar livre.
- **Código ao vivo:** cerca de 14 linhas, todas em `src/desviador_turtlesim.cpp`. O resto do arquivo já vem pronto.

### Onde cada conceito aparece na tela

| Conceito | O que a turma vê | Ferramenta | Passo |
|---|---|---|---|
| Imagem, container, volume | O prompt mudar para `root@...` e as pastas do repo dentro do container | `docker` | 2 |
| Nó | Cada programa vira uma caixa no grafo | `rqt_graph` | 3, 9 |
| Tópico | A seta entre as caixas, com o nome do tópico | `rqt_graph` | 3, 9 |
| Mensagem | O x e o y da tartaruga num gráfico ao vivo: ondas enquanto ela anda em círculo, linha reta quando para | `rqt_plot` | 5, 10 |
| Publicar | A tartaruga se mexer quando você publica no terminal | `ros2 topic pub` | 5 |
| Serviço | Uma tartaruga nova aparecer, a caneta ficar vermelha, a tela limpar | `ros2 service call` | 6 |
| Parâmetro | A cor do fundo mudar ao arrastar uma barra; a tartaruga mudar de comportamento ao trocar um valor | `rqt_reconfigure` | 6, 10 |
| Launch | Dois nós subindo com um comando só | `ros2 launch` | 11 |

### Quanto você vai codar

| Trecho | Passo | Onde no arquivo | Linhas | Tempo digitando |
|---|---|---|---|---|
| TODO 1: publisher e subscriber | 8 | Construtor | 4 | ~2 min |
| TODO 2: decidir a velocidade | 9 | `pose_callback` | 7 | ~2 min |
| TODO 3: parâmetros | 10 | Construtor + `pose_callback` | 3 novas + 3 trocas | ~2 min |

## Arquivos usados

| Arquivo | Para quê |
|---|---|
| `docker/Dockerfile` | A receita da imagem: ROS 2 Humble + pacotes + build do workspace |
| `docker/docker-compose.yaml` | Como o container sobe: volume, janelas (X11), rede |
| `workshop/ttbot/src/desviador_turtlesim.cpp` | Exercício com os 3 TODOs. É o arquivo que você completa ao vivo |
| `workshop/ttbot/src/desviador_turtlesim_solucao.cpp` | Versão pronta. Mostra o resultado no passo 1 e salva a aula se o seu código der erro |
| `workshop/ttbot/launch/turtlesim.launch.py` | Abre o turtlesim + o desviador |

## Antes da aula

- [ ] **Mandar para a turma, dias antes:** instalar o Docker, clonar o repositório e rodar `docker compose build` dentro de `docker/`. O build baixa vários GB, então precisa ser feito em casa, não na aula.
- [ ] **X11, no host de cada máquina** (de novo depois de cada reboot), antes do `docker compose up`. Com Docker, sem isso as janelas não abrem. No podman sem root (o seu caso), as janelas já abrem sem esse arquivo:
  ```bash
  touch /tmp/.docker.xauth
  xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f /tmp/.docker.xauth nmerge -
  ```
  Se o Docker já criou isso como pasta, apague com `sudo rm -rf /tmp/.docker.xauth` e repita.
- [ ] **GPU:** no Docker, `gpus: all` exige placa NVIDIA e NVIDIA Container Toolkit. Sem isso o container não sobe. Quem não tiver comenta `gpus: all` e as duas linhas `NVIDIA_*` do compose. O turtlesim não precisa de GPU.
- [ ] **Testar na sua máquina.** Dentro do container, compile primeiro: o container só tem o código da época em que foi criado, e sem o build o comando seguinte falha com `executable not found`.
  ```bash
  cd ~/workshop_ws && colcon build --packages-select ttbot && source install/setup.bash
  ros2 launch ttbot turtlesim.launch.py no:=desviador_turtlesim_solucao
  ```
  Abra também `rqt_graph`, `rqt_plot` e `rqt_reconfigure` uma vez e treine os ajustes dos passos 3, 5 e 6.
- [ ] **Ensaiar a aula inteira uma vez, cronometrando.** Depois do ensaio, volte o exercício ao estado original: `git checkout workshop/ttbot/src/desviador_turtlesim.cpp`.

### 10 minutos antes de começar

1. No host: `cd docker && docker compose up -d`.
2. Deixe um terminal no host (**H**) e abra outros 3 com `docker exec -it ros_workshop bash` (**T1**, **T2**, **T3**).
3. No T2, compile. É obrigatório: sem isso o passo 1 falha, e o primeiro build ao vivo fica lento.
   ```bash
   cd ~/workshop_ws && colcon build --packages-select ttbot && source install/setup.bash
   ```
   No T1 e no T3, rode só `cd ~/workshop_ws && source install/setup.bash`.
4. No VS Code, abra `workshop/ttbot/src/desviador_turtlesim.cpp` e aumente a fonte (Ctrl + =).
5. Arrume a tela para caberem lado a lado: a janela do turtlesim, um terminal e uma janela gráfica (`rqt_graph`, `rqt_plot` ou `rqt_reconfigure`).
6. Deixe este guia aberto no celular ou em outra tela.

## Roteiro

| Passo | Tempo | O que acontece | Na tela | Você digita código? |
|---|---|---|---|---|
| 1 | 0–2 | Mostrar o resultado final | turtlesim | Não |
| 2 | 2–6 | Docker: imagem, container, volume | terminal | Não |
| 3 | 6–9 | Nós e tópicos: turtlesim + teclado | `rqt_graph` | Não |
| 4 | 9–12 | O mesmo sistema pelo terminal | terminal | Não |
| 5 | 12–15 | Mensagens ao vivo e publicar na mão | `rqt_plot` | Não |
| 6 | 15–19 | Serviços e parâmetros | turtlesim, `rqt_reconfigure` | Não |
| 7 | 19–20 | Tour pelo `desviador_turtlesim.cpp` | editor | Não |
| 8 | 20–22 | TODO 1: publisher e subscriber | editor | Sim, 4 linhas |
| 9 | 22–25 | TODO 2: a decisão, compilar e rodar | `rqt_graph` | Sim, 7 linhas |
| 10 | 25–28 | TODO 3: parâmetros do nosso nó | `rqt_reconfigure`, `rqt_plot` | Sim, 3 linhas + 3 trocas |
| 11 | 28–29 | Launch file | turtlesim | Não |
| 12 | 29–30 | Fechamento | | Não |

**Se estiver atrasado:** pule o `interface show` do passo 4, o `set_pen` do passo 6 e o passo 10 inteiro (os parâmetros já apareceram no passo 6). **Se sobrar tempo:** faça o desafio 1 ao vivo.

---

### Passo 1: mostrar o resultado (0–2 min)

**Objetivo:** a turma ver aonde vai chegar.

**Rode:**
```bash
# T1
ros2 launch ttbot turtlesim.launch.py no:=desviador_turtlesim_solucao
```

**Fale:**
> "Essa tartaruga está andando sozinha e desviando das paredes. Quem decide para onde ela vai é um programa de umas 14 linhas, em C++, que a gente vai escrever hoje. Mas antes: como isso está rodando no meu computador?"

Deixe rodar uns 20 s. Dê **Ctrl+C no T1**.

---

### Passo 2: Docker (2–6 min)

**Objetivo:** a turma entender imagem, container e volume, e saber entrar no ambiente.

**Fale:**
> "O ROS 2 Humble precisa de Ubuntu 22.04 e de centenas de pacotes. Instalar isso em cada computador, cada um com um sistema diferente, dá problema. O Docker resolve isso: empacota o ambiente inteiro, e todo mundo roda exatamente o mesmo."

**Mostre** `docker/Dockerfile` (1 min), apontando três partes:
1. `FROM osrf/ros:humble-desktop-full`: partimos de uma imagem que já tem o ROS 2.
2. Os `apt-get install`: os pacotes extras (turtlesim, Gazebo, TurtleBot3...).
3. `colcon build`: já compila o nosso código dentro da imagem.

> "O Dockerfile é a receita. O `docker compose build` segue a receita e gera uma **imagem**, que é o ambiente pronto, guardado. Vocês fizeram isso em casa."

**Mostre** `docker/docker-compose.yaml`, apontando duas linhas:
1. `volumes: - ..:/root/workshop_ws/src`: a pasta do repositório aparece dentro do container.
2. `DISPLAY` e `/tmp/.X11-unix`: deixam as janelas (turtlesim, Gazebo) abrirem na sua tela.

**Rode:**
```bash
# H
docker images
docker ps
```
> "Aqui está a imagem. E aqui está um **container** rodando: é a imagem ligada, como um programa aberto. Dá para ter vários containers da mesma imagem."

```bash
# H
docker exec -it ros_workshop bash
```
O prompt muda para `root@...`.
> "Agora estou dentro do container. Daqui para frente, tudo roda aqui dentro."

```bash
# dentro do container (nesse mesmo terminal)
ls ~/workshop_ws/src/workshop
```
> "São as mesmas pastas do repositório no meu computador. Esse é o **volume**: o que eu editar no VS Code aparece aqui dentro na hora. Edito fora, compilo e rodo dentro."

```bash
exit
```
> "O `exit` sai do container, mas ele continua rodando. Para desligar de vez: `docker compose down`. Para ligar: `docker compose up -d`."

---

### Passo 3: nós e tópicos, no grafo (6–9 min)

**Objetivo:** a turma **ver** dois nós conversando por um tópico.

**Rode:**
```bash
# T1
ros2 run turtlesim turtlesim_node
```
> "Esse é um **nó**: um programa do ROS. Ele desenha a tartaruga e espera comandos."

```bash
# T2
ros2 run turtlesim turtle_teleop_key
```
Clique no T2 e mova a tartaruga com as setas.
> "Esse é outro nó: lê o teclado e manda comandos de velocidade. São dois programas separados. Como eles se falam?"

```bash
# T3
rqt_graph &
```
A janela pode abrir pequena: maximize. Depois, dois ajustes para o grafo ficar legível no projetor:

1. No **segundo** campo de texto do topo (o filtro de tópicos, que vem com `/`), digite `/turtle1/cmd_vel,/turtle1/pose` e aperte Enter. Sem o filtro aparecem mais duas setas, `/turtle1/rotate_absolute/_action/...`, porque o teclado também usa uma *ação* do turtlesim (girar até um ângulo). Se alguém perguntar: é o terceiro tipo de comunicação, que aparece nas perguntas do fim.
2. Clique no botão de **ajustar** (o quadradinho com setas, logo à direita de *Fit*), para o grafo ocupar a janela.

Se o grafo estiver desatualizado, clique em **atualizar** (o primeiro botão, no canto superior esquerdo). Pode aparecer uma elipse vazia na borda esquerda: é um detalhe do `rqt_graph`, ignore.

**O que aparece:**
```
┌────────────────┐   /turtle1/cmd_vel   ┌────────────┐
│ /teleop_turtle │ ───────────────────▶ │ /turtlesim │
└────────────────┘                      └────────────┘
```

**Aponte** cada parte com o mouse:
> "Cada caixa é um **nó**. A seta é um **tópico**, o `/turtle1/cmd_vel`: um canal com nome. O teclado **publica** no canal, e o turtlesim **assina**. Um não conhece o outro, os dois só conhecem o nome do canal. Por isso dá para trocar o teclado por qualquer outro programa, e é isso que a gente vai fazer no fim da aula."

**Deixe o `rqt_graph` aberto**: ele volta no passo 9. Dê **Ctrl+C no T2** (o teclado) e clique em atualizar no `rqt_graph`.
> "Fechei o teclado, e a caixa sumiu do grafo."

---

### Passo 4: o mesmo sistema pelo terminal (9–12 min)

**Objetivo:** ler pelo terminal o que o grafo mostrou.

**Rode no T2, um por vez, e fale depois de cada um:**

```bash
ros2 node list
```
> "As caixas do grafo, em texto. O teclado sumiu. E esse nome estranho, `rqt_gui_py_node_...`, é o próprio `rqt_graph`: ele também é um nó, e é assim que ele enxerga o grafo."

```bash
ros2 topic list
```
> "Todos os tópicos, inclusive os que o grafo esconde por não terem ninguém do outro lado. Dois interessam: `/turtle1/cmd_vel`, por onde a tartaruga recebe ordens, e `/turtle1/pose`, onde ela conta onde está."

```bash
ros2 topic info /turtle1/cmd_vel
```
> "O tipo da mensagem é `Twist`. Tem 1 assinante, o turtlesim, e 0 publicadores, porque fechei o teclado."

```bash
ros2 interface show geometry_msgs/msg/Twist
```
> "O formato da **mensagem**: uma parte linear e uma angular, cada uma com x, y e z. A tartaruga só usa duas: `linear.x`, para frente, e `angular.z`, girar."

```bash
ros2 topic echo /turtle1/pose --once
```
> "Uma mensagem de pose: x e y em metros, e `theta`, para onde ela aponta, em radianos. A janela vai de 0 a 11 m. Ela manda isso umas 60 vezes por segundo."

---

### Passo 5: mensagens ao vivo e publicar na mão (12–15 min)

**Objetivo:** **ver** as mensagens chegando, e mover a tartaruga publicando você mesmo.

**Rode:**
```bash
# T3
ros2 run rqt_plot rqt_plot /turtle1/pose/x /turtle1/pose/y &
```
Abre um gráfico com duas linhas retas. Maximize a janela.

**Alargue a janela de tempo antes de publicar.** Por padrão o gráfico mostra só 1 segundo, curto demais para ver o círculo:
1. Clique na **cruz** da barra do gráfico (ferramenta de mover).
2. Segure o **botão direito** dentro do gráfico e arraste para a esquerda, até o eixo de baixo mostrar uns 5 a 10 segundos.
3. Clique na cruz de novo para soltar a ferramenta.

A largura fica assim enquanto a janela estiver aberta.

> "Esse gráfico desenha, ao vivo, o x e o y de cada mensagem que chega em `/turtle1/pose`. Ela está parada, então as linhas estão retas."

```bash
# T2
ros2 topic pub --rate 10 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0}, angular: {z: 1.8}}"
```
**Mostre** a tartaruga andando em círculo e o gráfico virando duas ondas.
> "Agora eu sou o teclado: publico 10 vezes por segundo 'anda a 2 m/s e gira a 1,8 rad/s'. Andar e girar ao mesmo tempo dá um círculo. No gráfico, o x e o y sobem e descem: é o círculo visto de lado."

Dê **Ctrl+C no T2**. A tartaruga **para sozinha** cerca de 1 s depois, e o gráfico volta a ficar reto.

> "Parei de publicar e ela parou. O turtlesim zera a velocidade se os comandos param de chegar por 1 s. É uma proteção: se o programa que manda os comandos travar, o robô para. Guardem isso para a aula 2."

Deixe o `rqt_plot` aberto: ele volta no passo 10.

---

### Passo 6: serviços e parâmetros (15–19 min)

**Objetivo:** **ver** as duas outras formas de conversar com um nó.

**Serviços:**
```bash
# T2
ros2 service list
```
> "Além de tópicos, o turtlesim oferece **serviços**. Tópico é um fluxo contínuo, sem resposta. Serviço é um pedido com resposta, como chamar uma função de outro programa."

```bash
# T2
ros2 service call /spawn turtlesim/srv/Spawn "{x: 2.0, y: 2.0, theta: 0.0, name: 'tartaruga2'}"
```
**Mostre** a tartaruga nova na janela e a resposta no terminal (`name='tartaruga2'`).
> "Pedi 'crie uma tartaruga em x=2, y=2' e recebi de volta o nome dela. Pedido e resposta."

```bash
# T2
ros2 topic list
```
> "A tartaruga nova ganhou os próprios tópicos: `/tartaruga2/cmd_vel` e `/tartaruga2/pose`. O mesmo nó agora controla duas, e cada uma tem o seu canal."

```bash
# T2
ros2 service call /turtle1/set_pen turtlesim/srv/SetPen "{r: 255, g: 0, b: 0, width: 5}"
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0}}"
```
> "Troquei a cor da caneta por um serviço e mandei um único comando. A tartaruga anda 1 s, deixa um risco vermelho e para."

**Parâmetros:**
```bash
# T3
ros2 run rqt_reconfigure rqt_reconfigure &
```
Maximize a janela e clique em **Refresh**, embaixo da lista da esquerda: ao abrir, a lista costuma mostrar só os nós do próprio rqt. Clique em `turtlesim`. Aparecem três barras: `background_b`, `background_g`, `background_r`.

**Arraste** a barra `background_r` e mostre o fundo mudando de cor na hora.
> "**Parâmetros** são as configurações de um nó. Dá para mudar com ele rodando, e ele reage na hora. Essas barras são as configurações do turtlesim."

Mostre que é a mesma coisa pelo terminal:
```bash
# T2
ros2 param set /turtlesim background_r 150
```
> "A janela é só uma interface para isso. Olhem a barra: ela andou sozinha para 150."

Deixe o `rqt_reconfigure` aberto: ele volta no passo 10. Limpe para o próximo passo:
```bash
# T2
ros2 service call /reset std_srvs/srv/Empty
```
> "O `/reset` é outro serviço: apaga tudo e volta a tartaruga para o meio. A tartaruga2 sumiu."

**Resumo para falar:**
> "Tópico: fluxo contínuo, ninguém responde. Serviço: pedido e resposta. Parâmetro: configuração do nó."

---

### Passo 7: tour pelo código (19–20 min)

**Objetivo:** a turma entender o esqueleto antes de você digitar.

**Fale:**
> "Agora vamos substituir o teclado por um programa nosso, que olha a pose e decide sozinho."

**Mostre** `src/desviador_turtlesim.cpp` no editor, de cima para baixo:

1. **Comentário do topo:** o que o nó assina e o que publica.
2. **`#include`s:** um por tipo de mensagem, mais o `rclcpp`, a biblioteca do ROS 2 para C++.
3. **`class DesviadorTurtlesim : public rclcpp::Node`:** todo nó é uma classe que herda de `Node`. É uma caixa do `rqt_graph`.
4. **Construtor:** onde o nó se prepara. Mostre os TODOs 1 e 3, vazios.
5. **`pose_callback`:** é chamada sozinha a cada pose nova, ~60 vezes por segundo. Mostre o TODO 2.
6. **`parede_a_frente`:** já vem pronta. Olha um ponto 1 m à frente da tartaruga e diz se ele cai fora da janela.
7. **Constantes `DISTANCIA`, `VELOCIDADE`, `VELOCIDADE_GIRO`:** os valores que vamos usar por enquanto.
8. **`main`:** inicia o ROS, cria o nó e fica em `spin`, esperando mensagens.

> "A tartaruga não tem sensor. Então a função `parede_a_frente` faz o papel de um: um pouco de trigonometria para ver se tem parede logo à frente. Ela já está pronta. A gente vai escrever a parte de ROS."

---

### Passo 8: TODO 1, publisher e subscriber (20–22 min)

**Objetivo:** conectar o nó aos dois tópicos, ou seja, desenhar as setas do grafo.

**Digite** no construtor, no lugar do comentário `TODO 1`:

```cpp
pub_ = create_publisher<geometry_msgs::msg::Twist>("turtle1/cmd_vel", 10);
sub_ = create_subscription<turtlesim::msg::Pose>(
  "turtle1/pose", 10,
  std::bind(&DesviadorTurtlesim::pose_callback, this, std::placeholders::_1));
```

**Fale, enquanto digita:**
> "Primeira linha: vou **publicar** mensagens `Twist` em `turtle1/cmd_vel`, igual ao teclado e ao `ros2 topic pub` de antes. O tipo vai entre os sinais de menor e maior, e o 10 é o tamanho da fila."

> "Segunda: vou **assinar** mensagens `Pose` de `turtle1/pose`. O `std::bind` diz: quando chegar uma mensagem, chame o `pose_callback` deste objeto, passando a mensagem no lugar do `_1`."

> "Cada uma dessas linhas vai virar uma seta no `rqt_graph`."

Ainda não compile: falta a decisão.

---

### Passo 9: TODO 2, decidir, compilar e rodar (22–25 min)

**Objetivo:** a tartaruga andar sozinha, e o nosso nó aparecer no grafo.

**Digite** em `pose_callback`, no lugar do comentário `TODO 2`:

```cpp
geometry_msgs::msg::Twist cmd;
if (parede_a_frente(*pose, DISTANCIA)) {
  cmd.angular.z = VELOCIDADE_GIRO;  // parede: gira no lugar
} else {
  cmd.linear.x = VELOCIDADE;        // livre: anda para frente
}
pub_->publish(cmd);
```

**Fale, enquanto digita:**
> "Crio um comando. O `Twist` nasce todo zerado, então só preencho o que me interessa."

> "Tem parede a um metro? Gira no lugar. Caminho livre? Anda para frente."

> "E publico. Como essa função roda 60 vezes por segundo, a tartaruga reavalia o tempo todo."

**Rode** (o turtlesim do passo 3 continua aberto no T1):
```bash
# T2
cd ~/workshop_ws
colcon build --packages-select ttbot
source install/setup.bash
ros2 run ttbot desviador_turtlesim
```

O build leva cerca de 10 s. Enquanto isso:
> "O `colcon build` compila o pacote, e o `source` avisa o terminal que o pacote novo existe. Esqueceu o `source`? O `ros2 run` não acha o programa."

A tartaruga começa a andar e desviar.
> "É o código que a gente acabou de escrever dirigindo a tartaruga."

No `rqt_graph`, clique em atualizar e depois em ajustar. O filtro do passo 3 continua valendo.

**O que aparece:**
```
┌────────────┐     /turtle1/pose      ┌────────────┐
│            │ ─────────────────────▶ │            │
│ /turtlesim │                        │ /desviador │
│            │ ◀───────────────────── │            │
└────────────┘    /turtle1/cmd_vel    └────────────┘
```

> "O nosso nó apareceu no lugar do teclado, com as duas setas que a gente escreveu no TODO 1. É um laço fechado: a tartaruga conta onde está, o nosso nó decide, e manda o comando de volta. Quase todo robô funciona assim: sensor, decisão, comando."

**Se der errado:** erro de compilação, compare com `src/desviador_turtlesim_solucao.cpp`. Sem tempo para investigar, rode `ros2 run ttbot desviador_turtlesim_solucao` e siga a aula.

---

### Passo 10: TODO 3, parâmetros do nosso nó (25–28 min)

**Objetivo:** o nosso nó ganhar "barras" no `rqt_reconfigure`, como o turtlesim.

**Fale:**
> "No passo 6 a gente mudou a cor do fundo com o turtlesim rodando. Vamos dar o mesmo poder ao nosso nó: mudar a distância e a velocidade sem recompilar."

**Digite** no construtor, no lugar do comentário `TODO 3`:

```cpp
declare_parameter("distancia", 1.0);        // m
declare_parameter("velocidade", 1.5);       // m/s
declare_parameter("velocidade_giro", 1.5);  // rad/s
```

**Troque**, dentro do `pose_callback`:

| Antes | Depois |
|---|---|
| `DISTANCIA` | `get_parameter("distancia").as_double()` |
| `VELOCIDADE_GIRO` | `get_parameter("velocidade_giro").as_double()` |
| `VELOCIDADE` | `get_parameter("velocidade").as_double()` |

**Fale:**
> "`declare_parameter` cria o parâmetro com um valor padrão. E como eu leio o valor a cada mensagem, se alguém mudar, vale na hora."

**Rode:** Ctrl+C no T2 e:
```bash
# T2
cd ~/workshop_ws && colcon build --packages-select ttbot && source install/setup.bash
ros2 run ttbot desviador_turtlesim
```

No `rqt_reconfigure`, clique em **Refresh**. Agora aparece `desviador` na lista da esquerda. Clique nele: os parâmetros dele aparecem como campos de texto, abaixo dos do turtlesim (role a área da direita se precisar).
> "Aí estão os três parâmetros que a gente acabou de criar."

**Troque** `distancia` para `2.5` (digite e Enter).
> "Agora ela olha 2,5 m à frente, então começa a virar bem antes. Vejam os cantos do desenho ficando arredondados."

**Mostre** o `rqt_plot`:
> "No gráfico dá para ver: o x e o y vão e voltam, mas ficam sempre entre 0,5 e 10,5. A janela vai de 0 a 11, então a tartaruga nunca encosta na parede."

**Troque** `velocidade` para `4.0`.
> "E agora corre. No gráfico, as subidas e descidas ficam mais rápidas."

O mesmo pelo terminal, se quiser mostrar:
```bash
# T3
ros2 param set /desviador distancia 1.0
```
> "O campo na janela acompanhou: voltou para 1.0 sozinho."

---

### Passo 11: launch file (28–29 min)

**Objetivo:** subir tudo com um comando só.

Dê **Ctrl+C no T2** (o nó) e **no T1** (o turtlesim). Feche as janelas gráficas.

**Fale:**
> "Até agora foram dois terminais, um para cada nó. Num robô de verdade são dezenas de nós. Para isso existe o launch file."

**Rode:**
```bash
# T1
ros2 launch ttbot turtlesim.launch.py
```
> "Um comando subiu o turtlesim e o nosso nó, já com os parâmetros."

**Mostre** `launch/turtlesim.launch.py`: os dois `Node`, um para o turtlesim e outro para o nosso, com o bloco `parameters`.

> "O launch é em Python porque o ROS 2 não tem launch em C++, só em Python, XML ou YAML. Mas ele não é código do robô: só diz quais nós subir e com quais parâmetros."

---

### Passo 12: fechamento (29–30 min)

**Fale:**
> "Recapitulando:
> **imagem** é o ambiente pronto, **container** é a imagem rodando, e o **volume** liga a pasta do computador à do container;
> **nó** é um programa, uma caixa no grafo;
> **tópico** é um canal, uma seta no grafo, onde uns publicam e outros assinam;
> **mensagem** é o que passa no canal, como as poses que vimos no gráfico;
> **serviço** é pedido e resposta;
> **parâmetro** é configuração que muda com o nó rodando;
> **launch** sobe tudo de uma vez."

> "Na próxima aula, o mesmo nó num robô de verdade: um TurtleBot3, no simulador Gazebo, com um laser no lugar dessa conta de 'ponto à frente'. O código vai ser quase igual ao de hoje."

Passe os [desafios](#desafios-para-casa) e abra para perguntas.

---

## Problemas comuns na hora

| Sintoma | O que fazer |
|---|---|
| Container não sobe: `could not select device driver "nvidia"` | Comentar `gpus: all` e as linhas `NVIDIA_*` do compose |
| `ros2 launch ... no:=desviador_turtlesim_solucao` dá `executable not found` | O container é anterior ao código novo: `cd ~/workshop_ws && colcon build --packages-select ttbot && source install/setup.bash` |
| `touch: cannot touch '/tmp/.docker.xauth'` ou `Is a directory` | O Docker ou o podman criou uma pasta com esse nome: `sudo rm -rf /tmp/.docker.xauth` e repetir os comandos do xauth |
| Podman: build falha com `source: not found` | O podman ignora o `SHELL` do Dockerfile. Já corrigido no Dockerfile (usa `. setup.sh`); puxar a versão nova |
| turtlesim/rqt não abre: `cannot open display` ou `Authorization required` | Refazer o `/tmp/.docker.xauth` no host, ou rodar `xhost +local:` |
| `docker exec` diz que o container não existe | Ele não está rodando: `docker compose up -d` em `docker/` |
| `rqt_graph` vazio, desatualizado ou com o grafo minúsculo | Atualizar (primeiro botão do topo) e depois ajustar (à direita de *Fit*) |
| `rqt_graph` com setas `/turtle1/rotate_absolute/_action/...` | São da ação que o teclado usa. Filtro de tópicos: `/turtle1/cmd_vel,/turtle1/pose` |
| Elipse vazia na borda do `rqt_graph` | Detalhe do `rqt_graph`. Ignorar |
| `rqt_reconfigure` não mostra o `turtlesim` ou o `desviador` | Clicar em **Refresh**, embaixo da lista. O nó precisa estar rodando |
| `rqt_plot` mostra só um pedacinho de curva | A janela de tempo começa com 1 s. Cruz da barra do gráfico + arrastar com o botão direito para a esquerda (passo 5) |
| `rqt_plot` imprime `[ERROR] ... Malformed msg ... RotateAbsolute` | Ignorar: é um aviso do `rqt_plot` com o tópico de ação do turtlesim, e o gráfico funciona |
| Setas não movem a tartaruga | O teclado só funciona com o T2 selecionado: clique nele antes |
| Nosso nó roda, mas a tartaruga anda estranho ou não obedece | O teclado ainda está aberto e também publica em `/turtle1/cmd_vel`. Feche com Ctrl+C |
| `Package 'ttbot' not found` ou `No executable found` | Esqueceu de rodar `source install/setup.bash` depois do build |
| `ros2 topic list` (ou outro `ros2`) dá `RuntimeError: !rclpy.ok()` | Daemon do ROS travado: `ros2 daemon stop` e tentar de novo |
| Aviso `Oh no! I hit the wall!` | A tartaruga encostou na borda (normal com o teclado). Com o nosso nó, não deve acontecer |
| Tela cheia de riscos | `ros2 service call /clear std_srvs/srv/Empty` apaga os riscos. `/reset` também volta a tartaruga ao meio |

## Perguntas prováveis

- **Docker é uma máquina virtual?** Não. Uma VM simula um computador inteiro, com o próprio sistema. O container usa o sistema do computador e isola só os programas, por isso é bem mais leve e rápido de ligar.
- **Se eu apagar o container, perco meu código?** Não. O código está na pasta do repositório, no seu computador, e só aparece dentro do container pelo volume. O que se perde é o que foi criado só dentro do container, como o `build/` refeito na aula.
- **Por que a tartaruga para sozinha?** O turtlesim zera a velocidade se ficar 1 s sem receber comandos. Robôs reais têm o mesmo tipo de proteção, chamada *watchdog*. Na aula 2 a turma vê um simulador que não faz isso.
- **Dois nós podem publicar no mesmo tópico?** Podem, e o assinante recebe dos dois. Por isso o teclado precisa estar fechado quando o nosso nó roda: senão os dois brigam pelo controle.
- **O que é esse 10 no publisher e no subscriber?** É a QoS mais simples: guardar até 10 mensagens na fila. QoS são as regras de entrega de um tópico.
- **Por que `std::bind` e não uma lambda?** Os dois funcionam. O `std::bind` é o que aparece nos tutoriais oficiais do ROS 2.
- **C++ ou Python?** As APIs são quase iguais (`rclcpp` e `rclpy`). C++ é o padrão quando importa desempenho ou tempo de resposta. Python é mais rápido de escrever.
- **E ação, o que é?** O terceiro jeito de conversar, depois de tópico e serviço: uma tarefa longa, com progresso e possibilidade de cancelar. O turtlesim tem uma: `ros2 action list` mostra `/turtle1/rotate_absolute`.

## Desafios para casa

1. Girar para o lado certo: girar à esquerda ou à direita conforme a parede está de um lado ou do outro.
2. Controlar a `tartaruga2`: criar com o `/spawn` e rodar um segundo desviador para ela.
3. Desenhar um quadrado: um nó que, com um timer, alterna entre andar reto e girar 90°.
4. Trocar a cor da caneta toda vez que a tartaruga desvia, chamando o serviço `set_pen` de dentro do C++.
