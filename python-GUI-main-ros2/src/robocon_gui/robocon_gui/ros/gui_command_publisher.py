import json
import threading
from typing import Dict

from PyQt5.QtCore import QObject, pyqtSignal

import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String

from robocon_gui.core.gui_state import GuiState


class GuiCommandPublisher(QObject):
    telemetry_received = pyqtSignal(dict)

    def __init__(self, config):
        super().__init__()

        self.config = config
        self._shutdown = False
        self._owns_rclpy_context = False

        if not rclpy.ok():
            rclpy.init()
            self._owns_rclpy_context = True

        self.node = Node(config.ros.node_name)

        self.publisher = self.node.create_publisher(
            String,
            config.ros.gui_cmd_topic,
            config.ros.queue_size,
        )

        self.telemetry_subscriber = self.node.create_subscription(
            String,
            config.ros.telemetry_topic,
            self._on_telemetry_received,
            config.ros.queue_size,
        )

        self.executor = MultiThreadedExecutor()
        self.executor.add_node(self.node)

        self.executor_thread = threading.Thread(
            target=self.executor.spin,
            daemon=True,
        )
        self.executor_thread.start()

        self.node.get_logger().info(
            f"ROS2 GUI bridge aktif | publish={config.ros.gui_cmd_topic} | "
            f"subscribe={config.ros.telemetry_topic}"
        )

    def publish_state(self, state: GuiState) -> Dict[str, object]:
        packet = state.to_packet()

        msg = String()
        msg.data = json.dumps(packet)

        self.publisher.publish(msg)
        self.node.get_logger().info(f"GUI -> ROBOT | {msg.data}")

        return packet

    def _on_telemetry_received(self, msg: String) -> None:
        try:
            telemetry = json.loads(msg.data)
        except json.JSONDecodeError:
            telemetry = {
                "status": "INVALID_JSON",
                "raw": msg.data,
                "error": "Telemetry dari robot bukan JSON valid",
            }

        self.telemetry_received.emit(telemetry)

    def shutdown(self) -> None:
        if self._shutdown:
            return

        self._shutdown = True
        self.executor.shutdown()
        self.executor_thread.join(timeout=1.0)
        self.node.destroy_node()

        if self._owns_rclpy_context and rclpy.ok():
            rclpy.shutdown()
