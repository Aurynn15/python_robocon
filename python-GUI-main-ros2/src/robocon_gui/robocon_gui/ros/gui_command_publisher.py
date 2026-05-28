import json
from typing import Dict

import rospy
from PyQt5.QtCore import QObject, pyqtSignal
from std_msgs.msg import String

from robocon_gui.config import AppConfig
from robocon_gui.core.gui_state import GuiState


class GuiCommandPublisher(QObject):
    """
    ROS1 interface untuk GUI.

    Flow:
      GUI publish command  -> /robocon/gui_cmd       -> robot subscriber
      robot publish status -> /robocon/telemetry     -> GUI monitoring panel

    Message yang dipakai sengaja std_msgs/String berisi JSON agar tetap full Python
    dan tidak perlu custom message build seperti ROS2 robocon_interfaces/msg/GuiCommand.
    """

    telemetry_received = pyqtSignal(dict)

    def __init__(self, config: AppConfig):
        super().__init__()
        self.config = config

        if not rospy.core.is_initialized():
            rospy.init_node(
                config.ros.node_name,
                anonymous=True,
                disable_signals=True,
            )

        self.publisher = rospy.Publisher(
            config.ros.gui_cmd_topic,
            String,
            queue_size=config.ros.queue_size,
        )

        self.telemetry_subscriber = rospy.Subscriber(
            config.ros.telemetry_topic,
            String,
            self._on_telemetry_received,
        )

        rospy.loginfo(
            "GUI ROS1 interface aktif: publish=%s, subscribe=%s, type=std_msgs/String JSON",
            config.ros.gui_cmd_topic,
            config.ros.telemetry_topic,
        )

    def publish_state(self, state: GuiState) -> Dict[str, object]:
        """Convert GuiState menjadi JSON string, lalu publish ke topic command."""
        packet = state.to_packet()
        msg = String()
        msg.data = json.dumps(packet)

        self.publisher.publish(msg)
        rospy.loginfo("GUI -> ROBOT | %s", msg.data)
        return packet

    def _on_telemetry_received(self, msg: String) -> None:
        try:
            telemetry = json.loads(msg.data)
        except json.JSONDecodeError:
            telemetry = {
                "status": "INVALID_JSON",
                "raw": msg.data,
                "error": "Robot mengirim telemetry yang bukan JSON valid",
            }

        self.telemetry_received.emit(telemetry)

    def shutdown(self) -> None:
        try:
            self.telemetry_subscriber.unregister()
        except Exception:
            pass

        if not rospy.is_shutdown():
            rospy.signal_shutdown("Robocon GUI closed")
