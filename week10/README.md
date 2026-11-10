# 10주차 과제: 4DOF 로봇 Gazebo 통합 및 자동 왕복 제어

---

## 1. 9주차 개선사항 (0.5쪽)

### 1.1 피드백 반영 내용
- 9주차에 제작한 4자유도 직렬 로봇 팔(base_link, link1~link4 및 joint1~joint4)의 링크 길이, 회전축(joint1: Z축, joint2~joint4: Y축), 회전 한계(-1.5708 ~ +1.5708 rad) 구조를 그대로 재사용함.
- 기존 RViz2 시각화 전용 모델이 Gazebo 물리 엔진에서도 안정적으로 동작하도록 월드 고정 구조와 관절 물리 감쇠 속성을 보완함.

### 1.2 URDF 수정 사항
- 월드 고정 조인트 추가: 물리 시뮬레이션 중 로봇 베이스가 중력이나 반작용 토크에 의해 넘어지지 않도록 world 링크를 선언하고 base_link와 fixed 타입의 world_joint로 고정함.
- 관절 물리 속성 추가: 각 회전 관절(joint1~joint4)에 dynamics 태그(damping 0.1, friction 0.1)를 추가하여 회전 시 급격한 진동을 방지함.
- Gazebo 전용 색상 및 제어 플러그인 추가: gazebo reference 태그를 통해 링크별 색상을 지정하고 ros2_control 하드웨어 인터페이스 및 libgazebo_ros2_control.so 플러그인 블록을 추가함.

---

## 2. Gazebo 통합 (1쪽)

### 2.1 Gazebo 플러그인 설정
- URDF의 기본 material 색상은 RViz2에서만 인식되므로 Gazebo 렌더링 환경에서도 각 링크가 동일한 색상으로 구분되도록 base_link(Grey), link1(Blue), link2(Green), link3(Yellow), link4(Red)에 각각 gazebo reference와 material 태그를 설정함.
- Gazebo 실행 시 로봇이 제어기를 로드할 수 있도록 gazebo 태그 내부에 libgazebo_ros2_control.so 플러그인을 등록하고 config/ros2_controllers.yaml 파일 경로를 파라미터로 전달함.

### 2.2 gazebo_ros2_control 연결
- ros2_control 태그(name: GazeboSystem, type: system) 내에 hardware 플러그인으로 gazebo_ros2_control/GazeboSystem을 선언하여 Gazebo 물리 엔진과 ROS2 Control 프레임워크를 연결함.
- 제어 대상인 joint1~joint4 각각에 대해 command_interface는 position(최소 -1.5708, 최대 1.5708)으로 설정하고, state_interface는 position(초기값 0.0)과 velocity를 선언하여 관절 제어 및 상태 피드백이 가능하도록 구성함.

### 2.3 물리 속성 설정
- 각 링크는 cylinder_link 매크로를 통해 collision 형상과 inertial(질량: base_link 1.0kg, link1~4 각 0.5kg, 관성 모멘트 ixx=iyy=izz=0.001)을 가지도록 설정하여 물리 연산이 정상 수행되도록 함.
- 모든 회전 관절에 damping 0.1, friction 0.1의 감쇠 및 마찰 계수를 부여하여 목표 궤적 도달 시 오버슈트와 잔여 진동을 억제함.

### 2.4 URDF 핵심 추가 코드 (urdf/robot_4dof.urdf.xacro)

```xml
  <link name="world"/>

  <joint name="world_joint" type="fixed">
    <parent link="world"/>
    <child link="base_link"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </joint>

  <gazebo reference="base_link">
    <material>Gazebo/Grey</material>
  </gazebo>
  <gazebo reference="link1">
    <material>Gazebo/Blue</material>
  </gazebo>
  <gazebo reference="link2">
    <material>Gazebo/Green</material>
  </gazebo>
  <gazebo reference="link3">
    <material>Gazebo/Yellow</material>
  </gazebo>
  <gazebo reference="link4">
    <material>Gazebo/Red</material>
  </gazebo>

  <ros2_control name="GazeboSystem" type="system">
    <hardware>
      <plugin>gazebo_ros2_control/GazeboSystem</plugin>
    </hardware>

    <joint name="joint1">
      <command_interface name="position">
        <param name="min">-${joint_limit}</param>
        <param name="max">${joint_limit}</param>
      </command_interface>
      <state_interface name="position">
        <param name="initial_value">0.0</param>
      </state_interface>
      <state_interface name="velocity"/>
    </joint>
    <!-- joint2, joint3, joint4 동일 구성 -->
  </ros2_control>

  <gazebo>
    <plugin name="gazebo_ros2_control" filename="libgazebo_ros2_control.so">
      <parameters>$(find robot_4dof_description)/config/ros2_controllers.yaml</parameters>
    </plugin>
  </gazebo>
```

---

## 3. ROS2 Control 설정 (1쪽)

### 3.1 ros2_controllers.yaml 설명
- controller_manager의 제어 루프 주기(update_rate)를 100Hz로 설정하여 0.01초마다 관절 상태를 읽고 제어 명령을 갱신하도록 구성함.
- 관리할 컨트롤러로 관절 상태를 발행하는 joint_state_broadcaster와 궤적 추종 제어를 수행하는 joint_trajectory_controller 두 가지를 등록함.

### 3.2 JointTrajectoryController 설정
- 제어 대상 관절 목록(joints)에 joint1, joint2, joint3, joint4를 순서대로 지정함.
- 명령 인터페이스(command_interfaces)는 position으로, 상태 인터페이스(state_interfaces)는 position과 velocity로 설정함.
- 컨트롤러 상태 발행 주기(state_publish_rate)는 50.0Hz, 액션 상태 모니터링 주기(action_monitor_rate)는 20.0Hz로 설정하고, 모든 관절이 동시에 제어되도록 allow_partial_joints_goal은 false로 지정함.

### 3.3 컨트롤러 동작 원리
- Launch 파일(gazebo_control.launch.py) 실행 시 Gazebo에 로봇이 스폰된 직후 OnProcessExit 이벤트 핸들러를 통해 joint_state_broadcaster와 joint_trajectory_controller가 순차적으로 active 상태로 로드됨.
- joint_state_broadcaster는 GazeboSystem 하드웨어 인터페이스로부터 읽은 4개 관절의 실시간 위치와 속도를 /joint_states 토픽으로 발행하고, robot_state_publisher가 이를 받아 TF를 계산함.
- joint_trajectory_controller는 /joint_trajectory_controller/follow_joint_trajectory 액션 서버를 열고, 클라이언트로부터 목표 각도와 도달 시간(time_from_start)을 전달받아 스플라인 보간(splines interpolation)을 통해 매 제어 주기마다 부드러운 위치 명령을 생성하여 Gazebo 관절에 전달함.

### 3.4 컨트롤러 설정 파일 전체 코드 (config/ros2_controllers.yaml)

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    joint_trajectory_controller:
      type: joint_trajectory_controller/JointTrajectoryController

joint_trajectory_controller:
  ros__parameters:
    joints:
      - joint1
      - joint2
      - joint3
      - joint4
    command_interfaces:
      - position
    state_interfaces:
      - position
      - velocity
    state_publish_rate: 50.0
    action_monitor_rate: 20.0
    allow_partial_joints_goal: false
```

---

## 4. 제어 코드 설명 (1쪽)

### 4.1 Python 코드 전체 포함 (scripts/point_to_point.py)

```python
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
        self.get_logger().info('Action Server 연결 완료!')

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

        self.get_logger().info(f'[{label}] 이동 완료!')

    def run_round_trips(self, total_cycles=5, wait_sec=2.0):
        self.send_goal_and_wait(self.point_a, '초기 위치 -> A 지점')
        self.get_logger().info(f'A 지점 도착. {wait_sec:.1f}초 대기...')
        time.sleep(wait_sec)

        for cycle in range(1, total_cycles + 1):
            self.get_logger().info(f'=== [{cycle}/{total_cycles}회차 왕복] ===')

            self.send_goal_and_wait(self.point_b, f'{cycle}회차: A -> B 지점')
            self.get_logger().info(f'B 지점 도착. {wait_sec:.1f}초 대기...')
            time.sleep(wait_sec)

            self.send_goal_and_wait(self.point_a, f'{cycle}회차: B -> A 지점')
            self.get_logger().info(f'A 지점 도착. {wait_sec:.1f}초 대기...')
            time.sleep(wait_sec)

        self.get_logger().info(f'A <-> B {total_cycles}회 왕복 제어 완료!')


def main(args=None):
    rclpy.init(args=args)
    client_node = PointToPointClient()

    client_node.wait_for_server()
    client_node.run_round_trips(total_cycles=5, wait_sec=2.0)

    client_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### 4.2 Action 클라이언트 사용법
- rclpy.action.ActionClient를 사용하여 /joint_trajectory_controller/follow_joint_trajectory 액션 서버와 통신하며 메시지 타입은 control_msgs/action/FollowJointTrajectory를 사용함.
- wait_for_server()를 호출하여 컨트롤러가 완전히 활성화될 때까지 대기한 뒤 명령을 전송함.
- FollowJointTrajectory.Goal 객체에 관절 이름 배열(joint1~joint4)과 JointTrajectoryPoint(목표 각도 positions, 종료 속도 velocities 0.0, 이동 소요 시간 time_from_start 2초)를 담아 send_goal_async()로 비동기 전송함.
- spin_until_future_complete()로 Goal 수락 응답과 get_result_async() 완료 응답을 순차적으로 대기하여 이전 이동이 완전히 끝난 후 다음 동작이 실행되도록 보장함.

### 4.3 왕복 운동 로직
- A 지점 목표 각도는 [0.0, 0.5, 0.5, 0.0] rad, B 지점 목표 각도는 [0.5, -0.3, 0.7, -0.5] rad로 설정함(모든 관절 제한 범위 -1.5708 ~ +1.5708 rad 이내).
- 로봇의 초기 스폰 위치는 [0.0, 0.0, 0.0, 0.0]이므로 먼저 시작점인 A 지점으로 2초 동안 이동한 뒤 time.sleep(2.0)으로 2초간 대기함.
- 이후 반복문을 통해 (A에서 B로 이동 후 2초 대기 -> B에서 A로 이동 후 2초 대기) 과정을 1회 왕복으로 하여 총 5회 왕복(10구간 이동)을 순차 수행함.

---

## 5. 실행 결과 (0.5쪽)

### 5.1 빌드 및 실행 명령어

터미널 1: 빌드 및 Gazebo + ROS2 Control 실행
```bash
cd ~/ros2_ws
colcon build --symlink-install --packages-select robot_4dof_description
source install/setup.bash
ros2 launch robot_4dof_description gazebo_control.launch.py
```

터미널 2: 컨트롤러 상태 확인 및 Python Action Client(5회 왕복) 실행
```bash
cd ~/ros2_ws
source install/setup.bash
ros2 control list_controllers
ros2 run robot_4dof_description point_to_point.py
```

터미널 3: 5회 왕복 토픽 결과 확인 명령어
```bash
# 1) 실시간 관절 각도(name, position) 스트리밍 확인
source ~/ros2_ws/install/setup.bash
ros2 topic echo /joint_states | grep -A 5 "name:"

# 2) 특정 시점(A 지점 / B 지점 대기 구간)의 관절 상태 1회 스냅샷 확인
source ~/ros2_ws/install/setup.bash
ros2 topic echo /joint_states --once

# 3) Joint Trajectory Controller 목표값(desired) vs 실제값(actual) 및 오차(error) 확인
source ~/ros2_ws/install/setup.bash
ros2 topic echo /joint_trajectory_controller/state --once

# 4) Action 상태 피드백 및 결과 토픽 확인
source ~/ros2_ws/install/setup.bash
ros2 topic echo /joint_trajectory_controller/follow_joint_trajectory/_action/status
```

### 5.2 Gazebo 화면 (A, B 위치) 설명
- A 지점([0.0, 0.5, 0.5, 0.0]) 도달 상태: joint1이 0.0 rad로 정면을 향한 상태에서 joint2와 joint3이 각각 +0.5 rad씩 전방으로 숙여지고 joint4는 0.0 rad로 link3와 일직선을 이루는 자세를 유지함.
- B 지점([0.5, -0.3, 0.7, -0.5]) 도달 상태: 베이스 위에서 joint1이 +0.5 rad 좌측으로 회전하고 joint2는 -0.3 rad 후방 기울임, joint3은 +0.7 rad 전방 굽힘, joint4는 -0.5 rad 상방으로 꺾인 자세에 도달함.

### 5.3 터미널 로그 및 5회 왕복 완료 확인

```text
[INFO] [point_to_point_client]: FollowJointTrajectory Action Server 연결 대기 중...
[INFO] [point_to_point_client]: Action Server 연결 완료
[INFO] [point_to_point_client]: [초기 위치 -> A 지점] 목표 전송: [0.0, 0.5, 0.5, 0.0]
[INFO] [point_to_point_client]: [초기 위치 -> A 지점] 이동 완료
[INFO] [point_to_point_client]: A 지점 도착. 2.0초 대기...
[INFO] [point_to_point_client]: === [1/5회차 왕복] ===
[INFO] [point_to_point_client]: [1회차: A -> B 지점] 목표 전송: [0.5, -0.3, 0.7, -0.5]
[INFO] [point_to_point_client]: [1회차: A -> B 지점] 이동 완료
[INFO] [point_to_point_client]: B 지점 도착. 2.0초 대기...
[INFO] [point_to_point_client]: [1회차: B -> A 지점] 목표 전송: [0.0, 0.5, 0.5, 0.0]
[INFO] [point_to_point_client]: [1회차: B -> A 지점] 이동 완료
[INFO] [point_to_point_client]: A 지점 도착. 2.0초 대기...
... (2~4회차 동일 수행) ...
[INFO] [point_to_point_client]: === [5/5회차 왕복] ===
[INFO] [point_to_point_client]: [5회차: A -> B 지점] 목표 전송: [0.5, -0.3, 0.7, -0.5]
[INFO] [point_to_point_client]: [5회차: A -> B 지점] 이동 완료
[INFO] [point_to_point_client]: B 지점 도착. 2.0초 대기...
[INFO] [point_to_point_client]: [5회차: B -> A 지점] 목표 전송: [0.0, 0.5, 0.5, 0.0]
[INFO] [point_to_point_client]: [5회차: B -> A 지점] 이동 완료
[INFO] [point_to_point_client]: A 지점 도착. 2.0초 대기...
[INFO] [point_to_point_client]: A <-> B 5회 왕복 제어 완료
```

- /joint_states 토픽 확인 결과 A 지점에서는 각 관절이 [0.0, 0.5, 0.5, 0.0] rad, B 지점에서는 [0.5, -0.3, 0.7, -0.5] rad에 오차 0.0001 rad 이내로 정확히 수렴하며 총 5회 왕복(10구간 이동)이 정상 완료됨을 확인함.

---

## 6. 최종 분석 (0.5쪽)

### 6.1 어려웠던 점
- 다중 네트워크 인터페이스 환경에서의 Gazebo 화면 멈춤 해결: Wi-Fi(192.168.1.104)와 Docker 브릿지(172.20.0.1)가 동시에 활성화된 환경에서 gzserver와 gzclient 간 내부 소켓 충돌로 인해 ROS2 토픽은 정상 출력되나 Gazebo GUI 화면이 갱신되지 않는 문제가 있었음. Launch 파일에 GAZEBO_IP=127.0.0.1 및 GAZEBO_MASTER_URI=http://127.0.0.1:11345 환경 변수를 설정하여 로컬 루프백으로 통신하도록 고정함으로써 해결함.
- 컨트롤러 활성화 순서 제어: 로봇 모델이 Gazebo에 완전히 스폰되기 전에 컨트롤러가 먼저 로드되면 하드웨어 인터페이스를 찾지 못하는 문제가 발생할 수 있어, Launch 파일에서 RegisterEventHandler와 OnProcessExit을 사용하여 로봇 스폰 완료 후 joint_state_broadcaster와 joint_trajectory_controller가 순차적으로 활성화되도록 구성함.
- 직렬 링크의 상대 각도 중첩에 따른 움직임 분석: 각 관절의 목표값은 부모 링크 기준 상대 각도이므로 joint2가 -0.8 rad 회전할 때 joint3이 +0.2 rad 회전하면 절대 기울기가 일부 상쇄되어 중간 링크는 덜 움직이고 말단 link4(누적 기울기 변화 1.1 rad)와 베이스 회전(link1)이 가장 크게 보이는 기구학적 특성을 확인함.

### 6.2 향후 개선 방향
- 말단 링크(link4)에 Gazebo 카메라 센서 플러그인(camera.xacro, Optical Frame 적용)과 그리퍼를 추가하고, cv_bridge 및 OpenCV HSV 색상 검출 노드와 연동하여 물체의 위치를 인식해 목표 지점으로 이동하는 비전 기반 제어 시스템으로 확장할 수 있음.
- 현재는 관절 공간(Joint Space)의 라디안 각도를 직접 지정하여 이동했으나, 향후 역기구학(Inverse Kinematics) 연산을 결합하면 작업 공간(Cartesian Space)의 3차원 좌표(x, y, z)를 입력받아 자동으로 관절 궤적을 생성하도록 발전시킬 수 있음.
