FROM osrf/ros:humble-desktop-full

SHELL ["/bin/bash", "-c"]

# Avoid interactive prompts during package installation
ARG DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    git \
    build-essential \
    micro \
    python3-dbg \
    python3-empy \
    python3-numpy \
    python3-setuptools \
    python3-pip \
    python3-venv \
    vim \
    net-tools \
    iputils-ping \
    xvfb \
    curl \
    mesa-utils \
    && rm -rf /var/lib/apt/lists/*


# Python scientific stack
RUN pip3 install --no-cache-dir --upgrade \
    scipy \
    matplotlib


RUN mkdir -p /root/workshop_ws/src/workshop



# Set the working directory
WORKDIR /root/workshop_ws
COPY . src/

RUN export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}') \
    && curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"\
    && dpkg -i /tmp/ros2-apt-source.deb 

RUN apt-get update && apt-get install -y \
    ros-humble-ament-cmake-pycodestyle \
    ros-humble-rqt-tf-tree \
    ros-humble-tf-transformations \
    ros-humble-navigation2 \
    ros-humble-slam-toolbox \
    ros-humble-robot-localization \
    ros-humble-rtabmap-ros \
    ros-humble-xacro \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-sensor-msgs-py 
    

# Initialize rosdep
RUN rosdep init || true
RUN rosdep update \
    && rosdep install -r --from-paths src -i -y --rosdistro humble \
    && pip3 install transforms3d \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean -qq

RUN source /opt/ros/humble/setup.bash \
    && colcon build --merge-install --symlink-install

RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc \
    && echo "source ~/workshop_ws/install/setup.bash" >> ~/.bashrc \
    && echo "source /usr/share/colcon_cd/function/colcon_cd.sh" >> ~/.bashrc \
    && echo "export _colcon_cd_root=/opt/ros/humble/" >> ~/.bashrc \
    && echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" >> ~/.bashrc
