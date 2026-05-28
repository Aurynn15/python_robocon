#!/usr/bin/env python3
import json
import random
from typing import Dict, List

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class RobotCommandSubscriber(Node):
    def __init__(self):
        super().__init__("robot_command_subscriber")

        self.status = "READY"
        self.color = "MERAH"
        self.checkpoints = []
        self.current_checkpoint = "-"
        self.error = None

        self.telemetry_pub = self.create_publisher(
            String,
            "/robocon/telemetry",
            10,
        )

        self.subscriber = self.create_subscription(
            String,
            "/robocon/gui_cmd",
            self.on_gui_command,
            10,
        )

        self.telemetry_timer = self.create_timer(
            1.0,
            self.publish_telemetry,
        )

        self.get_logger().info("Robot subscriber aktif: /robocon/gui_cmd")
        self.get_logger().info("Robot telemetry publisher aktif: /robocon/telemetry")

    def on_gui_command(self, msg: String) -> None:
        try:
            packet = json.loads(msg.data)
        except json.JSONDecodeError:
            self.get_logger().warning(f"Command dari GUI bukan JSON valid: {msg.data}")
            self.error = "INVALID_GUI_JSON"
            self.publish_telemetry()
            return

        cmd = packet.get("cmd")
        color = packet.get("color", self.color)
        checkpoints = packet.get("checkpoints", [])

        self.get_logger().info(f"Dari GUI | {packet}")

        if cmd == "START_OTONOM":
            self.start_otonom(color, checkpoints)
        elif cmd == "EMERGENCY_STOP":
            self.emergency_stop()
        elif cmd == "RESET":
            self.reset_robot()
        elif cmd == "CHECKPOINT_UPDATE":
            self.update_checkpoints(checkpoints)
        elif cmd == "COLOR_CHANGE":
            self.update_color_mode(color)
        elif cmd == "RETRY_CAMERA":
            self.retry_camera()
        else:
            self.get_logger().warning(f"Command belum dikenali: {cmd}")
            self.error = "UNKNOWN_COMMAND"

        self.publish_telemetry()

    def start_otonom(self, color: str, checkpoints: List[int]) -> None:
        self.status = "RUNNING"
        self.color = color
        self.checkpoints = checkpoints
        self.current_checkpoint = checkpoints[0] if checkpoints else "-"
        self.error = None
        self.get_logger().info(
            f"ACTION: start otonom | warna={color} | checkpoints={checkpoints}"
        )

    def emergency_stop(self) -> None:
        self.status = "EMERGENCY_STOP"
        self.error = None
        self.get_logger().warning("ACTION: emergency stop")

    def reset_robot(self) -> None:
        self.status = "READY"
        self.checkpoints = []
        self.current_checkpoint = "-"
        self.error = None
        self.get_logger().info("ACTION: reset robot")

    def update_checkpoints(self, checkpoints: List[int]) -> None:
        self.checkpoints = checkpoints
        self.current_checkpoint = checkpoints[0] if checkpoints else "-"
        self.error = None
        self.get_logger().info(f"ACTION: update checkpoints -> {checkpoints}")

    def update_color_mode(self, color: str) -> None:
        self.color = color
        self.error = None
        self.get_logger().info(f"ACTION: update color mode -> {color}")

    def retry_camera(self) -> None:
        self.error = None
        self.get_logger().info("ACTION: retry camera")

    def make_telemetry_packet(self) -> Dict[str, object]:
        return {
            "status": self.status,
            "battery": round(12.0 + random.random() * 0.6, 2),
            "mcu_temp": round(40.0 + random.random() * 5.0, 1),
            "xavier_temp": round(55.0 + random.random() * 6.0, 1),
            "current_checkpoint": self.current_checkpoint,
            "color": self.color,
            "error": self.error,
        }

    def publish_telemetry(self) -> None:
        packet = self.make_telemetry_packet()

        msg = String()
        msg.data = json.dumps(packet)

        self.telemetry_pub.publish(msg)
        self.get_logger().info(f"ROBOT -> GUI | {msg.data}")


def main(args=None):
    rclpy.init(args=args)
    node = RobotCommandSubscriber()

    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()