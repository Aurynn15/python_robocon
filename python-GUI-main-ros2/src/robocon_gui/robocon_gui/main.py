import sys

from PyQt5 import QtWidgets

from robocon_gui.config import CONFIG
from robocon_gui.ros.gui_command_publisher import GuiCommandPublisher
from robocon_gui.ui.main_window import RobotMainWindow


def main(args=None):
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    ros_node = GuiCommandPublisher(CONFIG)
    window = RobotMainWindow(CONFIG, ros_node)
    window.showMaximized()

    exit_code = app.exec_()
    ros_node.shutdown()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
