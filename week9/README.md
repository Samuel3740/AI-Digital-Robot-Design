# 4-DOF 로봇 팔 URDF 모델링 및 RViz2 시각화 (보고서 핵심 정리)

---

## 1. 로봇 설계 (0.5쪽)

- **설계 목표**: ROS 2 Humble 환경에서 4개의 독립적인 회전 관절(`joint1`~`joint4`)을 가진 4자유도(4-DOF) 직렬형 로봇 팔을 URDF/Xacro로 모델링하고, `joint_state_publisher_gui`와 `RViz2`를 연동하여 관절 제어 및 시각화를 구현함.
- **구조 특징**:
  - 바닥에 고정되는 `base_link` 위에 4개의 원통형 링크(`link1`~`link4`)를 직렬로 배치함.
  - 3차원 공간 운동이 가능하도록 첫 번째 관절(`joint1`)은 수평 회전(Z축, Yaw), 나머지 관절(`joint2`~`joint4`)은 상하 굴절(Y축, Pitch)로 설계함.
  - 모든 관절의 회전 범위는 요구사항에 맞춰 `-90° ~ +90°` (`-1.5708 ~ +1.5708 rad`)로 제한함.

---

## 2. URDF 코드 설명 (1쪽)

### 2.1 주요 태그 설명
- **`<link>`**: 로봇을 구성하는 강체(마디)를 정의하며, 하위 태그로 외형(`visual`), 충돌(`collision`), 물리 특성(`inertial`)을 포함함.
- **`<joint>`**: 부모 링크(`parent`)와 자식 링크(`child`) 사이의 연결 관계, 회전축(`axis`), 회전 제한(`limit`)을 정의함.
- **`<visual>`**: RViz2 화면에 표시되는 링크의 기하학적 형상(`<cylinder>`), 중심 위치(`<origin>`), 색상(`<material>`)을 지정함.
- **`<collision>`**: 물리 엔진이나 경로 계획 시 충돌 계산에 사용되는 영역을 정의함 (본 모델에서는 `visual`과 동일한 원통 형상 적용).
- **`<inertial>`**: 링크의 질량(`<mass>`)과 관성 모멘트 행렬(`<inertia ixx ... izz/>`) 등 동역학 시뮬레이션에 필요한 물리 속성을 정의함.

### 2.2 좌표계 설정 방법
- **링크 중심 오프셋 (`<visual>`, `<collision>`, `<inertial>`의 `<origin>`)**:
  - URDF의 `<cylinder>`는 기본적으로 원통의 정중앙이 로컬 원점(`0 0 0`)에 생성됨.
  - 관절 회전 중심에 원통의 하단 끝점이 오도록, 원통 중심을 길이의 절반인 `xyz="0 0 ${length / 2.0}"` (`base_link`는 `0.05m`, `link1~4`는 `0.1m`)만큼 Z축으로 이동시킴.
- **관절 위치 설정 (`<joint>`의 `<origin>`)**:
  - 다음 관절이 이전 링크의 상단 끝점에 연결되도록, 부모 링크의 길이만큼 이동한 `xyz="0 0 ${base_length}"` (`0.1m`) 및 `xyz="0 0 ${link_length}"` (`0.2m`)로 설정함.

### 2.3 핵심 코드 발췌 (`urdf/robot_4dof.urdf.xacro`)

```xml
<!-- 원통형 링크 생성 매크로 (link, visual, collision, inertial) -->
<xacro:macro name="cylinder_link" params="name length radius mass color">
  <link name="${name}">
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

<!-- 회전 관절 정의 예시 (joint1, joint2) -->
<joint name="joint1" type="revolute">
  <parent link="base_link"/>
  <child link="link1"/>
  <origin xyz="0 0 ${base_length}" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
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
  [link2] (Green, 0.2m)
     │
   joint3 (Revolute, Y축 회전, -90° ~ +90°)
     ▼
  [link3] (Yellow, 0.2m)
     │
   joint4 (Revolute, Y축 회전, -90° ~ +90°)
     ▼
  [link4] (Red, 0.2m)
```

### 3.3 각 링크 및 관절 사양 표

**[링크 사양]**
| 링크 이름 | 형상 | 길이 (m) | 반지름 (m) | 중심 위치 (`origin xyz`) | 질량 (kg) | 색상 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `base_link` | Cylinder | 0.1 | 0.10 | `0 0 0.05` | 1.0 | Grey |
| `link1` | Cylinder | 0.2 | 0.03 | `0 0 0.10` | 0.5 | Blue |
| `link2` | Cylinder | 0.2 | 0.03 | `0 0 0.10` | 0.5 | Green |
| `link3` | Cylinder | 0.2 | 0.03 | `0 0 0.10` | 0.5 | Yellow |
| `link4` | Cylinder | 0.2 | 0.03 | `0 0 0.10` | 0.5 | Red |

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
- **원통 중심 좌표(`origin`)와 관절 위치 맞추기**: 처음에는 `<cylinder>`가 원점 기준으로 위아래 대칭 생성된다는 점을 간과하여 링크와 관절 위치가 겹치는 문제가 있었으나, 링크의 `<visual>` origin을 길이의 절반(`length / 2.0`)만큼 올리고 `<joint>` origin을 링크 끝점(`length`)에 두어 해결함.
- **`joint1`의 Z축 회전 확인**: 모든 관절이 `0 rad`일 때는 로봇 팔이 수직으로 일직선이어서 원통형인 `link1`을 Z축으로 회전시켜도 외형 변화가 눈에 잘 띄지 않았음. RViz2에서 `TF` 좌표계를 켜고 `joint2`~`joint4`를 기울인 상태에서 `joint1`을 조작하여 전체 팔이 수평 회전하는 것을 확인함.

### 4.2 향후 개선 방향
- **3D 메쉬 적용 및 그리퍼(Gripper) 추가**: 현재는 기본 원통 도형으로 모델링하였으나, 추후 CAD로 설계한 `.stl`/`.dae` 메쉬 파일을 적용하고 말단(`link4`) 끝에 물체를 잡는 그리퍼 관절을 추가할 수 있음.
- **MoveIt 2 및 Gazebo 연동**: 정의해 둔 `<collision>`과 `<inertial>` 속성을 바탕으로 Gazebo 물리 시뮬레이션이나 MoveIt 2 역기구학(IK) 경로 계획을 연동하여 원하는 목표 좌표로 로봇 팔을 제어하도록 확장할 수 있음.
