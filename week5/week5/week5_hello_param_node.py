import rclpy
from rclpy.node import Node


class HelloNode(Node):
    def __init__(self):
        super().__init__('hello_node')

        # 파라미터 선언
        self.declare_parameter('interval', 1.0)

        # 파라미터 값 가져오기
        interval = self.get_parameter('interval').value

        # 타이머 생성
        self.timer = self.create_timer(interval, self.timer_callback)

    def timer_callback(self):
        # 로거 객체를 호출해 메시지 출력
        self.get_logger().info('Hello ROS2')



def main(args=None):
    rclpy.init(args=args)

    node = HelloNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()