# robocon_gui/ros2_gui_publisher.py

import json
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


DATA_DIR = Path(
    "/home/lucymayreel/Downloads/robocon_gui_ros/python_robocon/python-GUI-main-ros1/src/robocon_gui/robocon_gui/core/kirim/src/gui_publis/gui_publis/data"
)

JSON_FILE = DATA_DIR / "json" / "gui_state.json"
DAT_FILE = DATA_DIR / "dat" / "gui_state.dat"


class GuiCommandPublisher(Node):
    def __init__(self):
        super().__init__("gui_command_publisher")

        self.publisher_ = self.create_publisher(
            String,
            "/gui/command",
            10
        )

        # Publish berkala setiap 1 detik
        self.timer = self.create_timer(1.0, self.publish_current_state)

        self.get_logger().info("GUI publisher aktif.")
        self.get_logger().info(f"Membaca data dari: {JSON_FILE}")

    def read_packet_from_json(self):
        """
        Membaca state terakhir dari file:
        data/json/gui_state.json
        """

        if not JSON_FILE.exists():
            self.get_logger().warn(f"File JSON belum ada: {JSON_FILE}")
            return None

        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                packet = json.load(f)

            return packet

        except json.JSONDecodeError as e:
            self.get_logger().error(f"Format JSON rusak: {e}")
            return None

        except Exception as e:
            self.get_logger().error(f"Gagal membaca JSON: {e}")
            return None

    def publish_current_state(self):
        """
        Dipanggil timer setiap 1 detik.
        Ambil data dari file JSON, lalu kirim ke ROS.
        """

        packet = self.read_packet_from_json()

        if packet is None:
            return

        msg = String()
        msg.data = json.dumps(packet, ensure_ascii=False)

        self.publisher_.publish(msg)

        self.get_logger().info(f"GUI FILE -> ROS -> ROBOT: {msg.data}")

    def publish_state(self, state):
        """
        Method ini boleh tetap ada kalau masih dipanggil dari GUI.
        Tapi sumber utama sekarang dari file JSON.
        """

        packet = {
            "cmd": state.cmd,
            "color": state.color_mode,
            "checkpoints": state.selected_checkpoints(),
            "status": state.robot_status,
        }

        msg = String()
        msg.data = json.dumps(packet, ensure_ascii=False)

        self.publisher_.publish(msg)

        self.get_logger().info(f"GUI STATE -> ROS -> ROBOT: {msg.data}")

        return packet


def main(args=None):
    rclpy.init(args=args)

    node = GuiCommandPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("GUI publisher dihentikan.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()