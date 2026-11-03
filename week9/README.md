# 4-DOF 로봇 팔 URDF 모델링 및 RViz2 시각화 (보고서 핵심 정리)

---

## 1. 로봇 설계 (0.5쪽)

- **설계 목표**: ROS 2 Humble 환경에서 4개의 회전 관절(`joint1`~`joint4`)을 가진 4자유도(4-DOF) 직렬형 로봇 팔을 URDF/Xacro로 모델링하고, `joint_state_publisher_gui`와 `RViz2`를 연동하여 실시간 관절 제어 및 시각화를 구현함.
- **구조 특징**:
  - 바닥에 고정되는 `base_link` 위에 4개의 원통형 링크(`link1`~`link4`)를 직렬로 배치함.
  - 첫 번째 관절(`joint1`)은 베이스 위에서 수평 회전(Z축, Yaw)하고, 상하로 꺾이는 나머지 관절(`joint2`~`joint4`, Y축 Pitch) 연결부(`link2`~`link4`의 원점)에는 가로 방향 원통형 구동부 형상을 추가하여 회전 시에도 링크가 끊어지지 않고 자연스럽게 이어지도록 설계함.
  - 모든 관절의 회전 범위는 `-90° ~ +90°` (`-1.5708 ~ +1.5708 rad`)로 제한함.

---

## 2. URDF 코드 설명 (1쪽)

### 2.1 주요 태그 설명 (강의자료 25~26p 연계)
- **`<link>`**: 로봇을 구성하는 강체(마디)를 정의하며, 하위 태그로 외형(`visual`), 충돌(`collision`), 물리 특성(`inertial`)을 포함함.
- **`<joint>`**: 부모 링크(`parent`)와 자식 링크(`child`) 사이의 연결 위치(`origin`), 회전축(`axis`), 운동 한계(`limit`: 도달 범위 `lower/upper`, 최대 토크 `effort`, 최대 속도 `velocity`)를 정의함.
- **`<visual>`**: RViz2 화면에 표시되는 링크의 기하학적 형상(`<cylinder>`), 위치·자세(`<origin>`), 색상(`<material>`)을 지정함.
- **`<collision>`**: 경로 계획이나 시뮬레이션 시 충돌 계산에 사용되는 영역을 정의함.
- **`<inertial>`**: 링크의 질량(`<mass>`)과 관성 모멘트(`<inertia>`)를 정의하며, 동역학 시뮬레이션에서 모터 과부하나 진동을 방지하기 위한 핵심 물리 파라미터임.

### 2.2 좌표계 설정 방법
- **링크 본체 중심 이동 (`xyz="0 0 ${length / 2.0}"`)**:
  - URDF의 `<cylinder>`는 원통의 정중앙이 원점(`0 0 0`)에 생성되므로, 관절 회전 중심에 원통 하단이 오도록 중심을 길이의 절반(`0.1m`)만큼 Z축 위로 이동시킴.
- **관절 구동부 회전 배치 (`xyz="0 0 0" rpy="1.5708 0 0"`)**:
  - 상하로 굴절되는 `link2`~`link4`의 시작점(`0 0 0`)에만 `<xacro:if>` 조건문으로 작은 원통을 배치하고 Roll(X축) 방향으로 `90°`(`1.5708 rad`) 회전시켜, Y축 회전 관절과 축 방향이 일치하는 구동부 형상을 표현함.
- **다음 관절 연결 위치 (`<joint>`의 `origin xyz="0 0 ${link_length}"`)**:
  - 다음 관절이 이전 링크의 상단 끝점에 연결되도록 부모 링크 길이(`0.2m`)만큼 Z축으로 이동시켜 설정함.

### 2.3 핵심 코드 발췌 (`urdf/robot_4dof.urdf.xacro`)

```xml
<!-- 원통형 링크 및 관절 구동부 생성 -->
<xacro:macro name="cylinder_link" params="name length radius mass color use_joint_visual">
  <link name="${name}">
    <!-- Y축 회전 관절(joint2~4)에만 원통형 구동부 생성 -->
    <xacro:if value="${use_joint_visual}">
      <visual>
        <origin xyz="0 0 0" rpy="1.5708 0 0"/>
        <geometry>
          <cylinder radius="0.035" length="0.07"/>
        </geometry>
        <material name="${color}"/>
      </visual>
    </xacro:if>
    <!-- 링크 원통 본체 -->
    <visual>
      <origin xyz="0 0 ${length / 2.0}" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="${radius}" length="${length}"/>
      </geometry>
      <material name="${color}"/>
    </visual>
    <collision>
      <origin xyz="0 0 ${length / 2.0}" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="${radius}" length="${length}"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 ${length / 2.0}" rpy="0 0 0"/>
      <mass value="${mass}"/>
      <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.001"/>
    </inertial>
  </link>
</xacro:macro>

<!-- 회전 관절 정의 예시 -->
<joint name="joint2" type="revolute">
  <parent link="link1"/>
  <child link="link2"/>
  <origin xyz="0 0 ${link_length}" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>
  <limit lower="-${joint_limit}" upper="${joint_limit}" effort="10.0" velocity="1.0"/>
</joint>
```

---

## 3. 실행 방법 (0.5쪽)

### 3.1 빌드 및 실행 명령어
```bash
cd ~/ros2_ws
colcon build --symlink-install --packages-select robot_4dof_description
source install/setup.bash
ros2 launch robot_4dof_description display_robot.launch.py
```

### 3.2 4-DOF 구조 다이어그램
```text
[base_link] (고정 베이스, Grey, 0.1m)
     │
   joint1 (Revolute, Z축 회전, -90° ~ +90°)
     ▼
  [link1] (Blue, 0.2m)
     │
   joint2 (Revolute, Y축 회전, -90° ~ +90°)
     ▼
  [link2] (Green, 0.2m + 관절 구동부)
     │
   joint3 (Revolute, Y축 회전, -90° ~ +90°)
     ▼
  [link3] (Yellow, 0.2m + 관절 구동부)
     │
   joint4 (Revolute, Y축 회전, -90° ~ +90°)
     ▼
  [link4] (Red, 0.2m + 관절 구동부)
```

### 3.3 각 링크 및 관절 사양 표

**[링크 사양]**
| 링크 이름 | 본체 형상 | 길이 (m) | 반지름 (m) | 본체 중심 (`origin xyz`) | 질량 (kg) | 색상 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `base_link` | Cylinder | 0.1 | 0.10 | `0 0 0.05` | 1.0 | Grey |
| `link1` | Cylinder | 0.2 | 0.03 | `0 0 0.10` | 0.5 | Blue |
| `link2` | Cylinder (+구동부) | 0.2 | 0.03 | `0 0 0.10` | 0.5 | Green |
| `link3` | Cylinder (+구동부) | 0.2 | 0.03 | `0 0 0.10` | 0.5 | Yellow |
| `link4` | Cylinder (+구동부) | 0.2 | 0.03 | `0 0 0.10` | 0.5 | Red |

**[관절 사양]**
| 관절 이름 | 타입 | Parent → Child | 관절 위치 (`origin xyz`) | 회전축 (`axis`) | 회전 범위 (`rad` / `deg`) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `joint1` | `revolute` | `base_link` → `link1` | `0 0 0.1` | Z축 (`0 0 1`) | `-1.5708 ~ 1.5708` (-90° ~ +90°) |
| `joint2` | `revolute` | `link1` → `link2` | `0 0 0.2` | Y축 (`0 1 0`) | `-1.5708 ~ 1.5708` (-90° ~ +90°) |
| `joint3` | `revolute` | `link2` → `link3` | `0 0 0.2` | Y축 (`0 1 0`) | `-1.5708 ~ 1.5708` (-90° ~ +90°) |
| `joint4` | `revolute` | `link3` → `link4` | `0 0 0.2` | Y축 (`0 1 0`) | `-1.5708 ~ 1.5708` (-90° ~ +90°) |

---

## 4. 기타

### 4.1 어려웠던 점
- **원통 중심 좌표(`origin`)와 관절 벌어짐 해결**: 처음에 단순 원통만 연결했을 때는 관절을 ±90°로 꺾을 때 원통 끝단 모서리가 벌어져 떨어져 보이는 문제가 있었음. 이를 해결하기 위해 링크 본체 중심을 `length / 2.0`으로 이동시키고, 관절 원점(`0 0 0`)에 `rpy="1.5708 0 0"`으로 90° 눕힌 가로 원통형 구동부를 추가하여 회전 시에도 자연스럽게 이어지도록 개선함.
- **Z축 회전 관절(`joint1`)과 Y축 회전 관절(`joint2~4`)의 연결부 구분**: 모든 링크에 가로 원통형 구동부를 넣었을 때, Z축으로 회전하는 `base_link`와 `link1` 사이에서는 가로 원통의 아랫부분이 베이스에 파묻혀 반으로 잘려 보이는 현상이 있었음. `<xacro:if>` 조건문을 활용해 Y축으로 꺾이는 `link2`~`link4`에만 구동부가 생성되도록 수정하여 해결함.
- **다중 `<visual>` 태그 사용 시 색상 적용 문제**: 하나의 `<link>` 내부에 구동부와 본체 2개의 `<visual>` 태그를 작성했을 때, 첫 번째 `<visual>`의 `<material>` 색상으로 링크 전체 색상이 덮어씌워지는 RViz2 특성을 확인하고 두 `<visual>` 모두 `${color}` 변수를 참조하도록 수정하여 해결함.

### 4.2 향후 개선 방향 (강의자료 10주차 내용 연계)
- **카메라 비전(`camera.xacro`) 및 그리퍼 장착**: 10주차 강의에서 다룬 것처럼 말단 링크(`link4`) 끝에 RGB-D 카메라(Optical Frame 적용)와 그리퍼를 추가하고, `cv_bridge` 및 OpenCV HSV 색상 검출 노드를 연동하여 특정 색상의 물체를 인식하도록 확장할 수 있음.
- **Gazebo 시뮬레이션, `ros2_control`, MoveIt 통합**: 정의해 둔 `<collision>`, `<inertial>`, `<limit>` 파라미터를 바탕으로 Gazebo 물리 시뮬레이터와 `ros2_control` 하드웨어 인터페이스를 연결하고, MoveIt의 Motion Planning을 적용해 자율 조작(Manipulation) 시스템으로 발전시킬 수 있음.
