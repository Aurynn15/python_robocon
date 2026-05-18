import cv2
from typing import Optional

from PyQt5 import QtWidgets, QtGui, QtCore

from robocon_gui.config import AppConfig
from robocon_gui.core.gui_state import GuiState
from robocon_gui.ros.gui_command_publisher import GuiCommandPublisher
from robocon_gui.services.camera_service import CameraService
from robocon_gui.ui import styles


class RobotMainWindow(QtWidgets.QMainWindow):
    def __init__(self, config: AppConfig, ros_node: GuiCommandPublisher):
        super().__init__()
        self.config = config
        self.ros_node = ros_node
        self.state = GuiState(cmd=config.command.ready)
        self._suppress_publish = False
        self.ros_node.telemetry_received.connect(self._on_telemetry_received)

        self._setup_window()
        self._setup_camera()
        self._setup_timers()
        self._update_last_message_display()

    # ======================================================
    # SETUP
    # ======================================================
    def _setup_window(self) -> None:
        self.setWindowTitle(self.config.gui.title)
        self.setGeometry(100, 100, self.config.gui.width, self.config.gui.height)
        self.setMinimumSize(1200, 700)
        self.setStyleSheet(styles.global_styles())

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        self._build_ui(central_widget)

    def _setup_camera(self) -> None:
        self.camera = CameraService(self.config.camera.device_path)

    def _setup_timers(self) -> None:
        self.cam_timer = QtCore.QTimer()
        self.cam_timer.timeout.connect(self._update_frame)
        self.cam_timer.start(self.config.camera.fps_interval_ms)

    # ======================================================
    # UI BUILDER
    # ======================================================
    def _build_ui(self, central_widget) -> None:
        root = QtWidgets.QHBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)
        central_widget.setLayout(root)

        root.addWidget(self._build_left_panel(), 7)
        root.addWidget(self._build_right_panel(), 3)

    def _build_left_panel(self):
        panel = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QtWidgets.QLabel("🎥  ROBOCON 2026 — VISION CONTROL")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setStyleSheet("font-size: 18px; font-weight: 700; color: #38bdf8; padding: 6px 12px; background: rgba(56,189,248,0.08); border-radius: 8px; border-left: 4px solid #38bdf8;")
        layout.addWidget(header)

        top_row = QtWidgets.QHBoxLayout()
        top_row.setSpacing(12)
        top_row.addWidget(self._build_camera_widget(), alignment=QtCore.Qt.AlignTop)
        top_row.addWidget(self._build_checkpoint_panel(), alignment=QtCore.Qt.AlignTop)
        layout.addLayout(top_row)

        self.last_msg_label = QtWidgets.QLabel()
        self.last_msg_label.setStyleSheet("background: rgba(0,0,0,0.4); border: 1px solid #1e293b; border-radius: 10px; padding: 10px; font-size: 11px; color: #22d3ee; font-family: monospace;")
        self.last_msg_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.last_msg_label.setWordWrap(True)
        layout.addWidget(self.last_msg_label, 1)

        self.target_label = QtWidgets.QLabel("🎯  Target: BELUM ADA STATUS BALIK")
        self.target_label.setAlignment(QtCore.Qt.AlignCenter)
        self.target_label.setStyleSheet("background: rgba(239,68,68,0.2); border: 1px solid #7f1d1d; border-radius: 10px; padding: 10px; font-size: 14px; font-weight: 600; color: #fca5a5;")
        layout.addWidget(self.target_label)

        return panel

    def _build_camera_widget(self):
        cam_frame = QtWidgets.QFrame()
        cam_frame.setFixedSize(500, 400)
        cam_frame.setStyleSheet("QFrame { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; }")

        cam_layout = QtWidgets.QVBoxLayout(cam_frame)
        cam_layout.setContentsMargins(12, 12, 12, 12)
        cam_layout.setSpacing(10)

        cam_title = QtWidgets.QLabel("📷  LIVE CAM — BOX DETECTION")
        cam_title.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 600; padding-left: 4px;")
        cam_layout.addWidget(cam_title)

        self.video_label = QtWidgets.QLabel("🔌 MENUNGGU KAMERA...")
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.video_label.setMinimumHeight(280)
        self.video_label.setStyleSheet("background: #020617; border: 1px dashed #334155; border-radius: 10px; font-size: 11px; color: #475569;")
        cam_layout.addWidget(self.video_label, 1)

        return cam_frame

    def _build_checkpoint_panel(self):
        frame = QtWidgets.QFrame()
        frame.setFixedHeight(400)
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QtWidgets.QLabel("📍  CHECKPOINT TOGGLE")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 13px; font-weight: 700; color: #38bdf8; padding: 4px 0; border-bottom: 1px solid #1e293b;")
        layout.addWidget(title)

        grid_widget = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(grid_widget)
        grid.setSpacing(8)

        self.cp_buttons = []
        for i in range(12):
            btn = QtWidgets.QPushButton(f"CP {i + 1}")
            btn.setCheckable(True)
            btn.setStyleSheet(styles.cp_style_off())
            btn.toggled.connect(lambda checked, idx=i: self._on_checkpoint_toggle(idx, checked))
            row, col = divmod(i, 6)
            grid.addWidget(btn, row, col)
            self.cp_buttons.append(btn)

        layout.addWidget(grid_widget, 1)
        return frame

    def _build_right_panel(self):
        panel = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        self.status_label = QtWidgets.QLabel("🟢  STATUS: READY")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setStyleSheet(styles.status_style("#10b981", "#059669"))
        layout.addWidget(self.status_label)

        layout.addWidget(self._build_color_toggle())

        self.btn_retry = QtWidgets.QPushButton("🔄  RETRY KAMERA")
        self.btn_retry.setStyleSheet(styles.btn_retry_dim())
        self.btn_retry.clicked.connect(self._retry_camera)
        layout.addWidget(self.btn_retry)

        layout.addWidget(self._build_telemetry_panel())

        layout.addStretch()

        info = QtWidgets.QLabel("🤖  Robocon 2026\nROS1 rospy JSON Interface")
        info.setAlignment(QtCore.Qt.AlignCenter)
        info.setStyleSheet("background: rgba(59,130,246,0.1); border: 1px solid #3b82f6; border-radius: 10px; padding: 10px; font-size: 12px;")
        layout.addWidget(info)

        layout.addWidget(self._build_action_buttons())
        return panel

    def _build_color_toggle(self):
        frame = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QtWidgets.QLabel("🎨  MODE WARNA KOTAK")
        title.setStyleSheet("font-size: 12px; color: #94a3b8; font-weight: 600;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        self.btn_merah = QtWidgets.QPushButton("🔴  MODE MERAH")
        self.btn_merah.setCheckable(True)
        self.btn_merah.setChecked(True)
        self.btn_merah.setStyleSheet(styles.color_btn_style("red", True))
        self.btn_merah.toggled.connect(lambda checked: self._on_color_toggle("MERAH", checked))

        self.btn_biru = QtWidgets.QPushButton("🔵  MODE BIRU")
        self.btn_biru.setCheckable(True)
        self.btn_biru.setStyleSheet(styles.color_btn_style("blue", False))
        self.btn_biru.toggled.connect(lambda checked: self._on_color_toggle("BIRU", checked))

        layout.addWidget(self.btn_merah)
        layout.addWidget(self.btn_biru)
        return frame

    def _build_telemetry_panel(self):
        frame = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        title = QtWidgets.QLabel("📊  ROBOT TELEMETRY")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 12px; color: #38bdf8; font-weight: 700;")
        layout.addWidget(title)

        self.telemetry_status = QtWidgets.QLabel("Status: -")
        self.telemetry_battery = QtWidgets.QLabel("Battery: - V")
        self.telemetry_mcu_temp = QtWidgets.QLabel("MCU Temp: - °C")
        self.telemetry_xavier_temp = QtWidgets.QLabel("Xavier Temp: - °C")
        self.telemetry_checkpoint = QtWidgets.QLabel("Checkpoint: -")
        self.telemetry_error = QtWidgets.QLabel("Error: -")

        for label in [
            self.telemetry_status,
            self.telemetry_battery,
            self.telemetry_mcu_temp,
            self.telemetry_xavier_temp,
            self.telemetry_checkpoint,
            self.telemetry_error,
        ]:
            label.setStyleSheet("font-size: 12px; color: #e2e8f0; padding: 2px;")
            label.setWordWrap(True)
            layout.addWidget(label)

        return frame

    def _build_action_buttons(self):
        frame = QtWidgets.QWidget()
        col = QtWidgets.QVBoxLayout(frame)
        col.setSpacing(8)
        col.setContentsMargins(0, 0, 0, 0)

        self.btn_start = QtWidgets.QPushButton("▶  START OTONOM")
        self.btn_start.setStyleSheet(styles.btn_start_dim())
        self.btn_start.clicked.connect(self._start_robot)

        self.btn_stop = QtWidgets.QPushButton("⛔  EMERGENCY STOP")
        self.btn_stop.setStyleSheet(styles.btn_stop_dim())
        self.btn_stop.clicked.connect(self._stop_robot)

        self.btn_reset = QtWidgets.QPushButton("🔄  RESET")
        self.btn_reset.setStyleSheet(styles.btn_reset_style())
        self.btn_reset.clicked.connect(self._reset_robot)

        col.addWidget(self.btn_start)
        col.addWidget(self.btn_stop)
        col.addWidget(self.btn_reset)
        return frame

    # ======================================================
    # PUBLISH COMMAND
    # ======================================================
    def _publish_state(self) -> None:
        if self._suppress_publish:
            return
        packet = self.ros_node.publish_state(self.state)
        self._update_last_message_display(packet)

    def _update_last_message_display(self, msg=None) -> None:
        if msg is None:
            text = (
                "📡 LAST ROS MSG: std_msgs/String JSON\n"
                f"cmd: {self.state.cmd}\n"
                f"color: {self.state.color_mode}\n"
                f"checkpoints: {self.state.selected_checkpoints()}\n"
                f"status: {self.state.robot_status}"
            )
        else:
            text = (
                "📡 LAST ROS MSG: std_msgs/String JSON\n"
                f"cmd: {msg.get('cmd')}\n"
                f"color: {msg.get('color')}\n"
                f"checkpoints: {msg.get('checkpoints')}\n"
                f"status: {msg.get('status')}"
            )
        self.last_msg_label.setText(text)

    # ======================================================
    # EVENT HANDLERS
    # ======================================================
    def _on_checkpoint_toggle(self, idx: int, checked: bool) -> None:
        self.state.checkpoint_active[idx] = checked
        self.cp_buttons[idx].setStyleSheet(styles.cp_style_on() if checked else styles.cp_style_off())
        self.state.cmd = self.config.command.checkpoint_update
        self._publish_state()

    def _on_color_toggle(self, color: str, checked: bool) -> None:
        if not checked:
            return

        self.state.color_mode = color
        self._suppress_publish = True
        if color == "MERAH":
            self.btn_merah.setStyleSheet(styles.color_btn_style("red", True))
            self.btn_biru.setChecked(False)
            self.btn_biru.setStyleSheet(styles.color_btn_style("blue", False))
        else:
            self.btn_biru.setStyleSheet(styles.color_btn_style("blue", True))
            self.btn_merah.setChecked(False)
            self.btn_merah.setStyleSheet(styles.color_btn_style("red", False))
        self._suppress_publish = False

        self.state.cmd = self.config.command.color_change
        self._publish_state()

    def _set_action_state(self, active: Optional[str]) -> None:
        if active == "start":
            self.btn_start.setStyleSheet(styles.btn_start_active())
            self.btn_stop.setStyleSheet(styles.btn_stop_dim())
        elif active == "stop":
            self.btn_stop.setStyleSheet(styles.btn_stop_active())
            self.btn_start.setStyleSheet(styles.btn_start_dim())
        else:
            self.btn_start.setStyleSheet(styles.btn_start_dim())
            self.btn_stop.setStyleSheet(styles.btn_stop_dim())

    def _start_robot(self) -> None:
        self.state.robot_status = "OTONOM"
        self.state.cmd = self.config.command.start
        self.status_label.setText("🟢  STATUS: OTONOM")
        self.status_label.setStyleSheet(styles.status_style("#10b981", "#059669"))
        self._set_action_state("start")
        self._publish_state()

    def _stop_robot(self) -> None:
        self.state.robot_status = "STOPPED"
        self.state.cmd = self.config.command.stop
        self.status_label.setText("🔴  STATUS: STOPPED")
        self.status_label.setStyleSheet(styles.status_style("#ef4444", "#dc2626"))
        self._set_action_state("stop")
        self._publish_state()

    def _reset_robot(self) -> None:
        self.state.robot_status = "READY"
        self.state.cmd = self.config.command.reset
        self.state.reset_checkpoints()

        self._suppress_publish = True
        for btn in self.cp_buttons:
            btn.setChecked(False)
            btn.setStyleSheet(styles.cp_style_off())
        self._suppress_publish = False

        self.status_label.setText("🟡  STATUS: RESET")
        self.status_label.setStyleSheet(styles.status_style("#f59e0b", "#d97706"))
        self._set_action_state(None)
        self._publish_state()

    def _retry_camera(self) -> None:
        self.state.cmd = self.config.command.retry_camera
        self.btn_retry.setStyleSheet(styles.btn_retry_active())
        QtCore.QTimer.singleShot(800, lambda: self.btn_retry.setStyleSheet(styles.btn_retry_dim()))
        self._publish_state()
        self.camera.release()
        QtCore.QTimer.singleShot(500, self.camera.reconnect)

    # ======================================================
    # CAMERA + TELEMETRY
    # ======================================================
    def _update_frame(self) -> None:
        ret, frame = self.camera.read_rgb_frame()
        if not ret:
            self.video_label.setText("🔌 KAMERA TERPUTUS")
            return

        h, w = frame.shape[:2]
        qt_img = QtGui.QImage(frame.data, w, h, 3 * w, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qt_img).scaled(
            self.video_label.size(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation,
        )
        self.video_label.setPixmap(pixmap)


    def _on_telemetry_received(self, telemetry: dict) -> None:
        status = telemetry.get("status", "-")
        battery = telemetry.get("battery", "-")
        mcu_temp = telemetry.get("mcu_temp", "-")
        xavier_temp = telemetry.get("xavier_temp", "-")
        checkpoint = telemetry.get("current_checkpoint", "-")
        error = telemetry.get("error", "-")

        self.telemetry_status.setText(f"Status: {status}")
        self.telemetry_battery.setText(f"Battery: {battery} V")
        self.telemetry_mcu_temp.setText(f"MCU Temp: {mcu_temp} °C")
        self.telemetry_xavier_temp.setText(f"Xavier Temp: {xavier_temp} °C")
        self.telemetry_checkpoint.setText(f"Checkpoint: {checkpoint}")
        self.telemetry_error.setText(f"Error: {error}")

        self.target_label.setText(f"🎯  Robot feedback: {status} | CP: {checkpoint}")
        self.target_label.setStyleSheet(
            "background: rgba(16,185,129,0.18); border: 1px solid #047857; "
            "border-radius: 10px; padding: 10px; font-size: 14px; "
            "font-weight: 600; color: #a7f3d0;"
        )

    def closeEvent(self, event) -> None:
        self.cam_timer.stop()
        self.camera.release()
        self.ros_node.shutdown()
        cv2.destroyAllWindows()
        event.accept()
