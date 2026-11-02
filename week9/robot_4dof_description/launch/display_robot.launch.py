import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    # 패키지 경로 및 xacro, rviz 설정 파일 경로 가져오기
    pkg_share = get_package_share_directory('robot_4dof_description')
    xacro_file = os.path.join(pkg_share, 'urdf', 'robot_4dof.urdf.xacro')
    rviz_config_file = os.path.join(pkg_share, 'config', 'view_robot.rviz')

    # xacro 파일을 URDF로 변환
    robot_description = xacro.process_file(xacro_file).toxml()

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}]
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen'
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_file]
        ),
    ])
