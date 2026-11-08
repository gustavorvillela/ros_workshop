import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'robo_py'


def files(*patterns):
    """Arquivos que existem hoje na pasta (os que você criar entram no próximo colcon build)."""
    found = []
    for pattern in patterns:
        found += [f for f in glob(pattern) if os.path.isfile(f)]
    return found


setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), files('launch/*.py')),
        (os.path.join('share', package_name, 'worlds'), files('worlds/*.sdf')),
        (os.path.join('share', package_name, 'urdf'), files('urdf/*.xacro', 'urdf/*.urdf')),
        (os.path.join('share', package_name, 'config'), files('config/*.yaml', 'config/*.lua')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Gustavo Rocha Villela',
    maintainer_email='grvillela@cos.ufrj.br',
    description='Workshop em Python: desvio de obstáculos, robô com lidar e IMU e mapeamento autônomo',
    license='MIT',
    entry_points={
        'console_scripts': [
            'obstacle_avoider = robo_py.obstacle_avoider:main',
            'route_mapper = robo_py.route_mapper:main',
        ],
    },
)
