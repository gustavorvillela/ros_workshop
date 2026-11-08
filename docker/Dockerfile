FROM osrf/ros:jazzy-desktop-full

SHELL ["/bin/bash", "-c"]

# Evita perguntas interativas durante a instalação
ARG DEBIAN_FRONTEND=noninteractive

# Ferramentas gerais
RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    git \
    build-essential \
    gdb \
    micro \
    vim \
    curl \
    net-tools \
    iputils-ping \
    mesa-utils \
    python3-numpy \
    python3-scipy \
    python3-matplotlib \
    python3-transforms3d \
    && rm -rf /var/lib/apt/lists/*

# Atualiza a chave do repositório do ROS (evita falhas de apt por chave expirada)
RUN export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}') \
    && curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb" \
    && dpkg -i /tmp/ros2-apt-source.deb

# Pacotes ROS usados nas 3 aulas (Gazebo Harmonic, TurtleBot3, Cartographer)
RUN apt-get update && apt-get install -y \
    ros-jazzy-ros-gz \
    ros-jazzy-turtlebot3-gazebo \
    ros-jazzy-turtlebot3-cartographer \
    ros-jazzy-turtlebot3-teleop \
    ros-jazzy-cartographer-ros \
    ros-jazzy-nav2-map-server \
    ros-jazzy-teleop-twist-keyboard \
    ros-jazzy-turtlesim \
    ros-jazzy-rqt-graph \
    ros-jazzy-rqt-tf-tree \
    ros-jazzy-tf2-tools \
    ros-jazzy-xacro \
    ros-jazzy-joint-state-publisher-gui \
    && rm -rf /var/lib/apt/lists/*

ENV TURTLEBOT3_MODEL=burger

# Dependências declaradas nos package.xml do workshop
WORKDIR /root/workshop_ws
COPY workshop/ src/workshop/
RUN rosdep init || true
RUN apt-get update \
    && rosdep update --rosdistro jazzy \
    && rosdep install -r --from-paths src -i -y --rosdistro jazzy \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean -qq

# O código é montado em src/ pelo docker-compose; a compilação é feita dentro do contêiner
RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc \
    && echo "[ -f ~/workshop_ws/install/setup.bash ] && source ~/workshop_ws/install/setup.bash" >> ~/.bashrc \
    && echo "source /usr/share/colcon_cd/function/colcon_cd.sh" >> ~/.bashrc \
    && echo "export _colcon_cd_root=/opt/ros/jazzy/" >> ~/.bashrc \
    && echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" >> ~/.bashrc
