#!/usr/bin/env python3
import time

from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectoryPoint


class PointToPointClient(Node):

    def __init__(self):
        super().__init__('point_to_point_client')
        self._action_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/joint_trajectory_controller/follow_joint_trajectory'
        )
        self.joint_names = ['joint1', 'joint2', 'joint3', 'joint4']

        self.point_a = [0.0, 0.5, 0.5, 0.0]
        self.point_b = [0.5, -0.3, 0.7, -0.5]

    def wait_for_server(self):
        self.get_logger().info('FollowJointTrajectory Action Server 연결 대기 중...')
        self._action_client.wait_for_server()
        self.get_logger().info('Action Server 연결 완료')

    def send_goal_and_wait(self, target_positions, label, move_sec=2):
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = self.joint_names

        point = JointTrajectoryPoint()
        point.positions = [float(p) for p in target_positions]
        point.velocities = [0.0] * len(self.joint_names)
        point.time_from_start = Duration(sec=int(move_sec), nanosec=0)
        goal_msg.trajectory.points = [point]

        self.get_logger().info(f'[{label}] 목표 전송: {target_positions}')

        send_goal_future = self._action_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, send_goal_future)

        goal_handle = send_goal_future.result()
        get_result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, get_result_future)

        self.get_logger().info(f'[{label}] 이동 완료')

    def run_round_trips(self, total_cycles=5, wait_sec=2.0):
        self.send_goal_and_wait(self.point_a, '초기 위치 -> A 지점')
        self.get_logger().info(f'A 지점 도착. {wait_sec:.1f}초 대기')
        time.sleep(wait_sec)

        for cycle in range(1, total_cycles + 1):
            self.get_logger().info(f'=== [{cycle}/{total_cycles}회차 왕복] ===')

            self.send_goal_and_wait(self.point_b, f'{cycle}회차: A -> B 지점')
            self.get_logger().info(f'B 지점 도착. {wait_sec:.1f}초 대기')
            time.sleep(wait_sec)

            self.send_goal_and_wait(self.point_a, f'{cycle}회차: B -> A 지점')
            self.get_logger().info(f'A 지점 도착. {wait_sec:.1f}초 대기')
            time.sleep(wait_sec)

        self.get_logger().info(f'A <-> B {total_cycles}회 왕복 제어 완료')


def main(args=None):
    rclpy.init(args=args)
    client_node = PointToPointClient()

    client_node.wait_for_server()
    client_node.run_round_trips(total_cycles=5, wait_sec=2.0)

    client_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
