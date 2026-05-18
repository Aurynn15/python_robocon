#!/usr/bin/env python3
import json
import random
from typing import Dict, List

import rospy
from std_msgs.msg import String


class RobotCommandSubscriber:
    """
    Contoh node robot ROS1.

    Node ini menjadi subscriber/listener dari command GUI:
      subscribe: /robocon/gui_cmd

    Node ini juga publish data balik untuk monitoring GUI:
      publish:   /robocon/telemetry
    """

    def __init__(self):
        self.status = "READY"
        self.color = "MERAH"
        self.checkpoints = []  # type: List[int]
        self.current_checkpoint = "-"
        self.error = None

        self.telemetry_pub = rospy.Publisher(
            "/robocon/telemetry",
            String,
            queue_size=10,
        )

        self.subscriber = rospy.Subscriber(
            "/robocon/gui_cmd",
            String,
            self.on_gui_command,
        )

        self.telemetry_timer = rospy.Timer(
            rospy.Duration(1.0),
            self.publish_telemetry,
        )

        rospy.loginfo("Robot subscriber aktif: /robocon/gui_cmd")
        rospy.loginfo("Robot telemetry publisher aktif: /robocon/telemetry")

    def on_gui_command(self, msg: String) -> None:
        try:
            packet = json.loads(msg.data)
        except json.JSONDecodeError:
            rospy.logwarn("Command dari GUI bukan JSON valid: %s", msg.data)
            self.error = "INVALID_GUI_JSON"
            self.publish_telemetry()
            return

        cmd = packet.get("cmd")
        color = packet.get("color", self.color)
        checkpoints = packet.get("checkpoints", [])

        rospy.loginfo("Dari GUI | %s", packet)

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
            rospy.logwarn("Command belum dikenali: %s", cmd)
            self.error = "UNKNOWN_COMMAND"

        self.publish_telemetry()

    def start_otonom(self, color: str, checkpoints: List[int]) -> None:
        self.status = "RUNNING"
        self.color = color
        self.checkpoints = checkpoints
        self.current_checkpoint = checkpoints[0] if checkpoints else "-"
        self.error = None
        rospy.loginfo("ACTION: start otonom | warna=%s | checkpoints=%s", color, checkpoints)
        # TODO: panggil logic robot jalan otonom di sini.

    def emergency_stop(self) -> None:
        self.status = "EMERGENCY_STOP"
        self.error = None
        rospy.logwarn("ACTION: emergency stop")
        # TODO: matikan motor / aktuator dengan aman di sini.

    def reset_robot(self) -> None:
        self.status = "READY"
        self.checkpoints = []
        self.current_checkpoint = "-"
        self.error = None
        rospy.loginfo("ACTION: reset robot")
        # TODO: reset state robot di sini.

    def update_checkpoints(self, checkpoints: List[int]) -> None:
        self.checkpoints = checkpoints
        self.current_checkpoint = checkpoints[0] if checkpoints else "-"
        self.error = None
        rospy.loginfo("ACTION: update checkpoints -> %s", checkpoints)
        # TODO: simpan checkpoint tujuan robot di sini.

    def update_color_mode(self, color: str) -> None:
        self.color = color
        self.error = None
        rospy.loginfo("ACTION: update color mode -> %s", color)
        # TODO: ubah mode deteksi warna di sini.

    def retry_camera(self) -> None:
        self.error = None
        rospy.loginfo("ACTION: retry camera")
        # TODO: reconnect kamera robot kalau memang diperlukan.

    def make_telemetry_packet(self) -> Dict[str, object]:
        # Angka di bawah masih dummy untuk test GUI.
        # Nanti ganti dengan pembacaan sensor asli dari robot/microcontroller.
        return {
            "status": self.status,
            "battery": round(12.0 + random.random() * 0.6, 2),
            "mcu_temp": round(40.0 + random.random() * 5.0, 1),
            "xavier_temp": round(55.0 + random.random() * 6.0, 1),
            "current_checkpoint": self.current_checkpoint,
            "color": self.color,
            "error": self.error,
        }

    def publish_telemetry(self, event=None) -> None:
        packet = self.make_telemetry_packet()
        msg = String()
        msg.data = json.dumps(packet)
        self.telemetry_pub.publish(msg)
        rospy.loginfo("ROBOT -> GUI | %s", msg.data)


def main():
    rospy.init_node("robot_command_subscriber", anonymous=False)
    RobotCommandSubscriber()
    rospy.spin()


if __name__ == "__main__":
    main()
