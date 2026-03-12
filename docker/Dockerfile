FROM osrf/ros:humble-desktop-full

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
    && rm -rf /var/lib/apt/lists/*

# Install Gazebo
RUN apt-get install -y \
    ros-humble-ros-gz \
    && rm -rf /var/lib/apt/lists/*

# Python scientific stack
RUN pip3 install --no-cache-dir --upgrade \
    scipy \
    matplotlib


RUN mkdir -p /root/workshop_ws/src/workshop



# Set the working directory
WORKDIR /root/workshop_ws
COPY . src/


RUN apt-get install -y \
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

RUN /bin/bash -c 'source /opt/ros/humble/setup.bash \
  && colcon build --merge-install --symlink-install'

RUN /bin/sh -c 'echo ". /opt/ros/humble/setup.bash" >> ~/.bashrc' \
 && /bin/sh -c 'echo ". ~/workshop_ws/install/setup.bash" >> ~/.bashrc'
