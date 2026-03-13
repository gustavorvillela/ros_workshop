from setuptools import find_packages, setup

package_name = 'comms'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Gustavo Rocha Villela',
    maintainer_email='gustavo.villela@student-cs.fr',
    description='Package for comms simulation in the ROS2 workshop.',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'talker = comms.talker:main',
            'listener = comms.listener:main',
        ],
    },
)
