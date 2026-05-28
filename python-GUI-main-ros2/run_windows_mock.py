import sys
import json
from pathlib import Path

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

# Tambahkan path package agar Python Windows bisa menemukan robocon_gui
PROJECT_ROOT = Path(__file__).resolve().parent
GUI_PACKAGE_PATH = PROJECT_ROOT / "src" / "robocon_gui"
sys.path.insert(0, str(GUI_PACKAGE_PATH))

from robocon_gui.config import CONFIG
from robocon_gui.ui.main_window import RobotMainWindow


class MockRosNode(QObject):
    telemetry_received = pyqtSignal(dict)

    def publish_state(self, state):
        packet = state.to_packet()

        print("MOCK GUI -> ROBOT:")
        print(json.dumps(packet, indent=2))

        telemetry = {
            "status": "MOCK_RUNNING",
            "battery": 12.4,
            "mcu_temp": 42.0,
            "xavier_temp": 55.0,
            "current_checkpoint": 1,
            "error": None
        }

        QTimer.singleShot(
            300,
            lambda: self.telemetry_received.emit(telemetry)
        )

        return packet

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