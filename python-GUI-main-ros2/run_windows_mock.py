import json
import sys
from pathlib import Path

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, QTimer, pyqtSignal

# Tambahkan path package agar Python bisa menemukan robocon_gui saat run mock.
PROJECT_ROOT = Path(__file__).resolve().parent
GUI_PACKAGE_PATH = PROJECT_ROOT / "src" / "robocon_gui"
sys.path.insert(0, str(GUI_PACKAGE_PATH))

from robocon_gui.config import CONFIG
from robocon_gui.ui.main_window import RobotMainWindow


class MockRosNode(QObject):
    telemetry_received = pyqtSignal(dict)

    def publish_packet(self, packet):
        print("MOCK ROS2 GUI -> ROBOT:")
        print(json.dumps(packet, indent=2, ensure_ascii=False))

        telemetry = {
            "status": "MOCK_RECEIVED",
            "battery": 12.4,
            "mcu_temp": 42.0,
            "nuc_temp": 55.0,
            "current_checkpoint": packet.get("checkpoint", "-"),
            "last_cmd": packet.get("cmd"),
            "error": None,
        }
        QTimer.singleShot(250, lambda: self.telemetry_received.emit(telemetry))
        return dict(packet)

    # Kompatibilitas dengan kode lama.
    def publish_state(self, state):
        return self.publish_packet(state.to_packet())

    def shutdown(self):
        print("Mock shutdown")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    ros_node = MockRosNode()
    window = RobotMainWindow(CONFIG, ros_node)
    window.showMaximized()

    exit_code = app.exec_()
    ros_node.shutdown()
    sys.exit(exit_code)
