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
        # launch 폴더 안의 모든 .py 파일들을 패키지 설치 경로 복사
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
            # 터미널에서 'ros2 run week5 hello_param_node' 명령 시
            # week5/week5_hello_param_node.py의 main 함수 실행
            'hello_param_node = week5.week5_hello_param_node:main',
        ],
    },
)
