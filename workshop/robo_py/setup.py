import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'robo_py'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Gustavo Rocha Villela',
    maintainer_email='grvillela@cos.ufrj.br',
    description='Trilha Python: nós obstacle_avoider (Aula 1), route_mapper (Aula 3), color_masks (Aula 4) e cylinder_detector (Aula 5)',
    license='MIT',
    entry_points={
        'console_scripts': [
            'obstacle_avoider = robo_py.obstacle_avoider:main',
            'route_mapper = robo_py.route_mapper:main',
            'color_masks = robo_py.color_masks:main',
            'cylinder_detector = robo_py.cylinder_detector:main',
        ],
    },
)
