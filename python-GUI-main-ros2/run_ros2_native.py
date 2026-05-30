import sys
from pathlib import Path

from PyQt5 import QtWidgets

# Launcher langsung untuk ROS2 native, tanpa bergantung pada console_scripts setup.py.
PROJECT_ROOT = Path(__file__).resolve().parent
GUI_PACKAGE_PATH = PROJECT_ROOT / "src" / "robocon_gui"
sys.path.insert(0, str(GUI_PACKAGE_PATH))

from robocon_gui.config import CONFIG
from robocon_gui.ros.gui_command_publisher import GuiCommandPublisher
from robocon_gui.ui.main_window import RobotMainWindow


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    ros_node = GuiCommandPublisher(CONFIG)
    window = RobotMainWindow(CONFIG, ros_node)
    window.showMaximized()

    exit_code = app.exec_()
    ros_node.shutdown()
    sys.exit(exit_code)
