from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'week5'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')
        )
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='samuel',
    maintainer_email='roysangjun@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'hello_param_node = week5.week5_hello_param_node:main',
        ],
    },
)
