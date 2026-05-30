import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
from PyQt5 import QtCore, QtGui, QtWidgets

from robocon_gui.config import AppConfig
from robocon_gui.core.gui_state import GuiState
from robocon_gui.services.camera_service import CameraService
from robocon_gui.ui import styles


class RobotMainWindow(QtWidgets.QMainWindow):
    """GUI Robocon 2026 dengan 2 page: Camera Monitoring dan Decision Training."""

    def __init__(self, config: AppConfig, ros_node: Any):
        super().__init__()
        self.config = config
        self.ros_node = ros_node
        self.state = GuiState(cmd=config.command.ready)

        self.camera: Optional[CameraService] = None
        self.camera_stream_active = True
        self._active_page = 0
        self._last_packet: Dict[str, object] = self.state.to_packet()

        self.grid_buttons: List[QtWidgets.QPushButton] = []
        self.weapon_buttons: List[QtWidgets.QPushButton] = []
        self.checkpoint_buttons: List[QtWidgets.QPushButton] = []
        self.grid_button_group: Optional[QtWidgets.QButtonGroup] = None

        self.data_dir = Path.home() / ".robocon_gui" / "data"
        self.json_dir = self.data_dir / "json"
        self.dat_dir = self.data_dir / "dat"
        self.json_dir.mkdir(parents=True, exist_ok=True)
        self.dat_dir.mkdir(parents=True, exist_ok=True)
        self.json_file = self.json_dir / "gui_state.json"
        self.dat_file = self.dat_dir / "gui_state.dat"

        if hasattr(self.ros_node, "telemetry_received"):
            self.ros_node.telemetry_received.connect(self._on_telemetry_received)

        self._setup_window()
        self._setup_camera()
        self._setup_timers()
        self._update_last_message_display(self._last_packet)
        self._append_log("GUI ready. Page 1 = camera, Page 2 = decision training.")

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
        self.cam_timer = QtCore.QTimer(self)
        self.cam_timer.timeout.connect(self._update_frame)
        self.cam_timer.start(self.config.camera.fps_interval_ms)

    # ======================================================
    # UI BUILDER
    # ======================================================
    def _build_ui(self, central_widget: QtWidgets.QWidget) -> None:
        root = QtWidgets.QVBoxLayout(central_widget)
        root.setContentsMargins(18, 18, 18, 14)
        root.setSpacing(12)

        self.title_bar = QtWidgets.QLabel("ABU ROBOCON 2026")
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setAlignment(QtCore.Qt.AlignCenter)
        root.addWidget(self.title_bar)

        self.pages = QtWidgets.QStackedWidget()
        self.pages.addWidget(self._build_camera_page())
        self.pages.addWidget(self._build_decision_page())
        root.addWidget(self.pages, 1)

        root.addLayout(self._build_bottom_nav())
        self._set_page(0)

    def _card(self, object_name: str = "Card") -> QtWidgets.QFrame:
        frame = QtWidgets.QFrame()
        frame.setObjectName(object_name)
        return frame

    def _section_title(self, text: str) -> QtWidgets.QLabel:
        label = QtWidgets.QLabel(text)
        label.setObjectName("SectionTitle")
        label.setAlignment(QtCore.Qt.AlignCenter)
        return label

    def _build_camera_page(self) -> QtWidgets.QWidget:
        page = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        left = QtWidgets.QVBoxLayout()
        left.setSpacing(12)
        left.addWidget(self._build_camera_card(), 1)
        left.addLayout(self._build_camera_controls())

        right = QtWidgets.QVBoxLayout()
        right.setSpacing(12)
        right.addWidget(self._build_log_card(), 1)
        right.addWidget(self._build_telemetry_card(), 1)

        layout.addLayout(left, 7)
        layout.addLayout(right, 5)
        return page

    def _build_camera_card(self) -> QtWidgets.QFrame:
        card = self._card()
        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        layout.addWidget(self._section_title("LIVE CAMERA — BOX / KFS MONITORING"))

        self.video_label = QtWidgets.QLabel("MENUNGGU KAMERA...")
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.video_label.setMinimumSize(560, 360)
        self.video_label.setStyleSheet(
            "background: #050a12; border: 1px solid #263850; border-radius: 12px; "
            "color: #7b8ca5; font-size: 16px; font-weight: 800;"
        )
        layout.addWidget(self.video_label, 1)
        return card

    def _build_camera_controls(self) -> QtWidgets.QHBoxLayout:
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(12)

        self.btn_reset_camera = QtWidgets.QPushButton("↻ RETRY / START CAMERA")
        self.btn_reset_camera.setStyleSheet(styles.action_button("camera_reset"))
        self.btn_reset_camera.clicked.connect(self._reset_or_start_camera)

        self.btn_stop_camera = QtWidgets.QPushButton("■ STOP STREAM CAMERA")
        self.btn_stop_camera.setStyleSheet(styles.action_button("camera_stop"))
        self.btn_stop_camera.clicked.connect(self._stop_camera_stream)

        row.addWidget(self.btn_reset_camera)
        row.addWidget(self.btn_stop_camera)
        return row

    def _build_log_card(self) -> QtWidgets.QFrame:
        card = self._card()
        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        layout.addWidget(self._section_title("COMMAND LOG"))

        self.last_msg_label = QtWidgets.QPlainTextEdit()
        self.last_msg_label.setReadOnly(True)
        self.last_msg_label.setMinimumHeight(230)
        layout.addWidget(self.last_msg_label, 1)
        return card

    def _build_telemetry_card(self) -> QtWidgets.QFrame:
        card = self._card()
        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)
        layout.addWidget(self._section_title("ROBOT TELEMETRY"))

        self.status_label = QtWidgets.QLabel("STATUS: READY")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setStyleSheet(styles.status_style("#10b981"))
        layout.addWidget(self.status_label)

        self.telemetry_status = QtWidgets.QLabel("Status: -")
        self.telemetry_battery = QtWidgets.QLabel("Battery: - V")
        self.telemetry_mcu_temp = QtWidgets.QLabel("MCU Temp: - °C")
        self.telemetry_xavier_temp = QtWidgets.QLabel("CPU/NUC Temp: - °C")
        self.telemetry_checkpoint = QtWidgets.QLabel("Checkpoint: -")
        self.telemetry_error = QtWidgets.QLabel("Error: -")
        self.target_label = QtWidgets.QLabel("Robot feedback: belum ada status balik")

        for label in [
            self.telemetry_status,
            self.telemetry_battery,
            self.telemetry_mcu_temp,
            self.telemetry_xavier_temp,
            self.telemetry_checkpoint,
            self.telemetry_error,
            self.target_label,
        ]:
            label.setWordWrap(True)
            label.setStyleSheet(
                "background: #09111d; border: 1px solid #22344e; border-radius: 7px; "
                "padding: 7px; color: #e6edf6; font-weight: 750;"
            )
            layout.addWidget(label)

        layout.addStretch()
        return card

    def _build_decision_page(self) -> QtWidgets.QWidget:
        page = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Proporsi dibuat mendekati desain Canva:
        # kiri grid besar, tengah weapon ramping, kanan panel decision.
        layout.addWidget(self._build_grid_panel(), 7)
        layout.addWidget(self._build_weapon_panel(), 1)
        layout.addWidget(self._build_decision_control_panel(), 7)
        return page

    def _build_grid_panel(self) -> QtWidgets.QFrame:
        card = self._card()
        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        grid_widget = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(2)
        grid.setVerticalSpacing(2)

        self.grid_buttons = []
        self.grid_button_group = QtWidgets.QButtonGroup(self)
        self.grid_button_group.setExclusive(True)

        for row in range(4):
            grid.setRowStretch(row, 1)
        for col in range(3):
            grid.setColumnStretch(col, 1)

        for number in range(1, 13):
            btn = QtWidgets.QPushButton(str(number))
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setMinimumSize(130, 120)
            btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            btn.setStyleSheet(styles.grid_button(False))
            btn.clicked.connect(lambda _=False, n=number: self._on_grid_clicked(n))
            row, col = divmod(number - 1, 3)
            grid.addWidget(btn, row, col)
            self.grid_button_group.addButton(btn, number)
            self.grid_buttons.append(btn)

        layout.addWidget(grid_widget, 1)
        return card

    def _build_weapon_panel(self) -> QtWidgets.QFrame:
        card = self._card()
        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        title = QtWidgets.QLabel("WEAPON")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet(
            "background: #142033; border: 1px solid #263850; border-radius: 18px; padding: 20px 4px; "
            "font-size: 18px; font-weight: 900; color: #e6edf6;"
        )
        layout.addWidget(title)

        self.weapon_buttons = []
        for slot in range(1, 5):
            btn = QtWidgets.QPushButton(str(slot))
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            btn.setStyleSheet(styles.weapon_button(False))
            btn.clicked.connect(lambda _=False, s=slot: self._on_weapon_clicked(s))
            layout.addWidget(btn)
            self.weapon_buttons.append(btn)

        return card

    def _build_decision_control_panel(self) -> QtWidgets.QFrame:
        card = self._card()
        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        self.btn_reset_micro = QtWidgets.QPushButton("↻ RESET MICRO / ROBOT")
        self.btn_reset_micro.setFixedHeight(92)
        self.btn_reset_micro.setStyleSheet(styles.action_button("reset"))
        self.btn_reset_micro.clicked.connect(self._reset_micro)
        layout.addWidget(self.btn_reset_micro)

        header_row = QtWidgets.QHBoxLayout()
        header_row.setSpacing(16)
        box_title = QtWidgets.QLabel("BOX KFS")
        cp_title = QtWidgets.QLabel("CHECKPOINT")
        for title in (box_title, cp_title):
            title.setAlignment(QtCore.Qt.AlignCenter)
            title.setFixedHeight(46)
            title.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            title.setStyleSheet(styles.panel_header())
        header_row.addWidget(box_title)
        header_row.addWidget(cp_title)
        layout.addLayout(header_row)

        mid = QtWidgets.QHBoxLayout()
        mid.setSpacing(16)

        box_col = QtWidgets.QVBoxLayout()
        box_col.setSpacing(12)
        self.btn_box_red = QtWidgets.QPushButton("MERAH")
        self.btn_box_blue = QtWidgets.QPushButton("BIRU")
        self.btn_box_red.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.btn_box_blue.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.btn_box_red.clicked.connect(lambda: self._on_box_color_clicked("MERAH"))
        self.btn_box_blue.clicked.connect(lambda: self._on_box_color_clicked("BIRU"))
        box_col.addWidget(self.btn_box_red, 1)
        box_col.addWidget(self.btn_box_blue, 1)
        mid.addLayout(box_col, 1)

        cp_col = QtWidgets.QVBoxLayout()
        cp_col.setSpacing(12)
        self.checkpoint_buttons = []
        for cp in (1, 2):
            btn = QtWidgets.QPushButton(f"CP {cp}")
            btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            btn.clicked.connect(lambda _=False, c=cp: self._on_checkpoint_clicked(c))
            cp_col.addWidget(btn, 1)
            self.checkpoint_buttons.append(btn)
        mid.addLayout(cp_col, 1)
        layout.addLayout(mid, 1)

        bottom = QtWidgets.QHBoxLayout()
        bottom.setSpacing(16)
        self.btn_start = QtWidgets.QPushButton("▶ START TRAINING")
        self.btn_stop = QtWidgets.QPushButton("⛔ EMERGENCY STOP")
        self.btn_start.setFixedHeight(92)
        self.btn_stop.setFixedHeight(92)
        self.btn_start.setStyleSheet(styles.action_button("start"))
        self.btn_stop.setStyleSheet(styles.action_button("stop"))
        self.btn_start.clicked.connect(self._start_training)
        self.btn_stop.clicked.connect(self._emergency_stop)
        bottom.addWidget(self.btn_start)
        bottom.addWidget(self.btn_stop)
        layout.addLayout(bottom)

        self._refresh_box_styles()
        self._refresh_checkpoint_styles()
        return card

    def _build_bottom_nav(self) -> QtWidgets.QHBoxLayout:
        nav = QtWidgets.QHBoxLayout()
        nav.setSpacing(10)

        footer = QtWidgets.QLabel("ABUROBOCON 2026")
        footer.setObjectName("TitleBar")
        footer.setAlignment(QtCore.Qt.AlignCenter)
        nav.addWidget(footer, 1)

        self.btn_page_camera = QtWidgets.QPushButton("1")
        self.btn_page_decision = QtWidgets.QPushButton("2")
        self.btn_page_camera.clicked.connect(lambda: self._set_page(0))
        self.btn_page_decision.clicked.connect(lambda: self._set_page(1))
        nav.addWidget(self.btn_page_camera)
        nav.addWidget(self.btn_page_decision)
        return nav

    # ======================================================
    # UI STATE HELPERS
    # ======================================================
    def _set_page(self, index: int) -> None:
        self._active_page = index
        self.pages.setCurrentIndex(index)
        self.btn_page_camera.setStyleSheet(styles.nav_button(index == 0))
        self.btn_page_decision.setStyleSheet(styles.nav_button(index == 1))
        self.title_bar.setText(
            "ABU ROBOCON 2026 — CAMERA & MONITORING"
            if index == 0
            else "ABU ROBOCON 2026"
        )

    def _set_status(self, text: str, color: str) -> None:
        self.status_label.setText(text)
        self.status_label.setStyleSheet(styles.status_style(color))

    def _set_active_button(self, buttons: List[QtWidgets.QPushButton], active_index: Optional[int], style_func) -> None:
        for idx, btn in enumerate(buttons):
            is_active = active_index == idx
            if btn.isCheckable():
                btn.blockSignals(True)
                btn.setChecked(is_active)
                btn.blockSignals(False)
            btn.setStyleSheet(style_func(is_active))

    def _refresh_box_styles(self) -> None:
        self.btn_box_red.setStyleSheet(styles.box_button("red", self.state.kfs_color == "MERAH"))
        self.btn_box_blue.setStyleSheet(styles.box_button("blue", self.state.kfs_color == "BIRU"))

    def _refresh_checkpoint_styles(self) -> None:
        for idx, btn in enumerate(self.checkpoint_buttons, start=1):
            btn.setStyleSheet(styles.checkpoint_button(self.state.selected_checkpoint == idx))

    # ======================================================
    # ROS2 PUBLISH + HISTORY
    # ======================================================
    def _publish_packet(self, packet: Dict[str, object]) -> None:
        packet.setdefault("source", "gui")
        packet.setdefault("mode", self.state.mode)
        packet.setdefault("status", self.state.robot_status)
        packet.setdefault("kfs_color", self.state.kfs_color)
        packet.setdefault("color", self.state.kfs_color)
        packet["timestamp"] = datetime.now().isoformat(timespec="seconds")

        if hasattr(self.ros_node, "publish_packet"):
            sent_packet = self.ros_node.publish_packet(packet)
        elif hasattr(self.ros_node, "publish_state"):
            sent_packet = self.ros_node.publish_state(self.state)
            sent_packet.update(packet)
        else:
            sent_packet = packet

        self._last_packet = dict(sent_packet)
        self._save_packet_to_file(self._last_packet)
        self._update_last_message_display(self._last_packet)
        self._append_log(f"PUBLISH {self._last_packet.get('cmd')}: {json.dumps(self._last_packet, ensure_ascii=False)}")

    def _save_packet_to_file(self, packet: Dict[str, object]) -> None:
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(packet, f, indent=2, ensure_ascii=False)

        with open(self.dat_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(packet, ensure_ascii=False) + "\n")

    def _update_last_message_display(self, packet: Optional[Dict[str, object]] = None) -> None:
        packet = packet or self._last_packet
        topic = self.config.ros.gui_cmd_topic
        pretty = json.dumps(packet, indent=2, ensure_ascii=False)
        self.last_msg_label.setPlainText(f"LAST ROS2 MSG → {topic}\nstd_msgs/msg/String JSON\n\n{pretty}")

    def _append_log(self, text: str) -> None:
        if not hasattr(self, "last_msg_label"):
            return
        now = datetime.now().strftime("%H:%M:%S")
        current = self.last_msg_label.toPlainText()
        line = f"[{now}] {text}"
        if not current:
            self.last_msg_label.setPlainText(line)
            return
        self.last_msg_label.appendPlainText(line)

    # ======================================================
    # DECISION EVENT HANDLERS
    # ======================================================
    def _on_grid_clicked(self, grid_number: int) -> None:
        self.state.selected_grid = grid_number
        self.state.cmd = self.config.command.move_to_grid
        self._set_active_button(self.grid_buttons, grid_number - 1, styles.grid_button)
        self._publish_packet(
            self.state.build_packet(
                self.config.command.move_to_grid,
                grid=grid_number,
                target=f"GRID_{grid_number}",
            )
        )

    def _on_weapon_clicked(self, weapon_slot: int) -> None:
        self.state.selected_weapon_slot = weapon_slot
        self.state.cmd = self.config.command.take_weapon
        self._set_active_button(self.weapon_buttons, weapon_slot - 1, styles.weapon_button)
        self._publish_packet(
            self.state.build_packet(
                self.config.command.take_weapon,
                weapon_slot=weapon_slot,
                target=f"WEAPON_RACK_{weapon_slot}",
            )
        )

    def _on_box_color_clicked(self, color: str) -> None:
        self.state.kfs_color = color
        self.state.cmd = self.config.command.set_kfs_color
        self._refresh_box_styles()
        self._publish_packet(
            self.state.build_packet(
                self.config.command.set_kfs_color,
                kfs_color=color,
                color=color,
                box_color=color,
            )
        )

    def _on_checkpoint_clicked(self, checkpoint: int) -> None:
        self.state.selected_checkpoint = checkpoint
        self.state.cmd = self.config.command.set_checkpoint
        self._refresh_checkpoint_styles()
        self._publish_packet(
            self.state.build_packet(
                self.config.command.set_checkpoint,
                checkpoint=checkpoint,
            )
        )

    def _start_training(self) -> None:
        self.state.robot_status = "TRAINING_RUNNING"
        self.state.cmd = self.config.command.start_training
        self._set_status("STATUS: TRAINING RUNNING", "#10b981")
        self.btn_start.setStyleSheet(styles.action_button("start", True))
        self.btn_stop.setStyleSheet(styles.action_button("stop", False))
        self._publish_packet(self.state.build_packet(self.config.command.start_training))

    def _emergency_stop(self) -> None:
        self.state.robot_status = "STOPPED"
        self.state.cmd = self.config.command.emergency_stop
        self._set_status("STATUS: EMERGENCY STOP", "#ef4444")
        self.btn_start.setStyleSheet(styles.action_button("start", False))
        self.btn_stop.setStyleSheet(styles.action_button("stop", True))
        self._publish_packet(self.state.build_packet(self.config.command.emergency_stop))

    def _reset_micro(self) -> None:
        self.state.reset_decision()
        self._set_active_button(self.grid_buttons, None, styles.grid_button)
        self._set_active_button(self.weapon_buttons, None, styles.weapon_button)
        self._refresh_checkpoint_styles()
        self._refresh_box_styles()
        self.btn_start.setStyleSheet(styles.action_button("start", False))
        self.btn_stop.setStyleSheet(styles.action_button("stop", False))
        self._set_status("STATUS: READY / STANDBY", "#f59e0b")
        self._publish_packet(self.state.build_packet(self.config.command.reset_robot, status="READY"))

    # ======================================================
    # CAMERA CONTROL
    # ======================================================
    def _reset_or_start_camera(self) -> None:
        self.camera_stream_active = True
        if self.camera is not None:
            self.camera.release()
            QtCore.QTimer.singleShot(250, self.camera.reconnect)
        if not self.cam_timer.isActive():
            self.cam_timer.start(self.config.camera.fps_interval_ms)
        self.video_label.setText("MEMULAI ULANG KAMERA...")
        self._append_log("Camera stream restarted locally. Tidak publish command ke robot.")

    def _stop_camera_stream(self) -> None:
        self.camera_stream_active = False
        if self.cam_timer.isActive():
            self.cam_timer.stop()
        if self.camera is not None:
            self.camera.release()
        self.video_label.clear()
        self.video_label.setText("STREAM CAMERA STOPPED\nTekan RETRY / START CAMERA untuk mulai lagi")
        self._append_log("Camera stream stopped locally. Tidak publish command ke robot.")

    def _update_frame(self) -> None:
        if not self.camera_stream_active or self.camera is None:
            return

        ret, frame = self.camera.read_rgb_frame()
        if not ret or frame is None:
            self.video_label.setText("KAMERA TERPUTUS")
            return

        height, width = frame.shape[:2]
        bytes_per_line = 3 * width
        qt_img = QtGui.QImage(frame.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qt_img).scaled(
            self.video_label.size(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation,
        )
        self.video_label.setPixmap(pixmap)

    # ======================================================
    # TELEMETRY
    # ======================================================
    def _on_telemetry_received(self, telemetry: dict) -> None:
        status = telemetry.get("status", "-")
        battery = telemetry.get("battery", "-")
        mcu_temp = telemetry.get("mcu_temp", "-")
        cpu_temp = telemetry.get("xavier_temp", telemetry.get("nuc_temp", "-"))
        checkpoint = telemetry.get("current_checkpoint", telemetry.get("checkpoint", "-"))
        error = telemetry.get("error", "-")

        self.telemetry_status.setText(f"Status: {status}")
        self.telemetry_battery.setText(f"Battery: {battery} V")
        self.telemetry_mcu_temp.setText(f"MCU Temp: {mcu_temp} °C")
        self.telemetry_xavier_temp.setText(f"CPU/NUC Temp: {cpu_temp} °C")
        self.telemetry_checkpoint.setText(f"Checkpoint: {checkpoint}")
        self.telemetry_error.setText(f"Error: {error}")
        self.target_label.setText(f"Robot feedback: {status} | CP: {checkpoint}")
        self._append_log(f"TELEMETRY: {json.dumps(telemetry, ensure_ascii=False)}")

    def closeEvent(self, event) -> None:
        if hasattr(self, "cam_timer"):
            self.cam_timer.stop()
        if self.camera is not None:
            self.camera.release()
        if hasattr(self.ros_node, "shutdown"):
            self.ros_node.shutdown()
        cv2.destroyAllWindows()
        event.accept()
