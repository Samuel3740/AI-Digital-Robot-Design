from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    interval = LaunchConfiguration('interval')

    return LaunchDescription([
        DeclareLaunchArgument(
            'interval',
            default_value='1.0',
            description='Hello ROS2 message interval'
        ),

        Node(
            package='week5',
            executable='hello_param_node',
            name='hello_node',
            parameters=[
                {'interval': interval}
            ]
        )
    ])