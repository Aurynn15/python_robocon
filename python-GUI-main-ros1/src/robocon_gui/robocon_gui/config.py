from dataclasses import dataclass, field


@dataclass(frozen=True)
class RosConfig:
    """Konfigurasi ROS1 untuk GUI di Jetson Xavier."""

    node_name: str = "robocon_gui_node"
    gui_cmd_topic: str = "/robocon/gui_cmd"
    telemetry_topic: str = "/robocon/telemetry"
    queue_size: int = 10


@dataclass(frozen=True)
class CameraConfig:
    device_path: str = "/dev/video0"
    fps_interval_ms: int = 30


@dataclass(frozen=True)
class GuiConfig:
    title: str = "Robocon 2026 - PRO"
    width: int = 1400
    height: int = 800


@dataclass(frozen=True)
class CommandConfig:
    ready: str = "READY"
    start: str = "START_OTONOM"
    stop: str = "EMERGENCY_STOP"
    reset: str = "RESET"
    retry_camera: str = "RETRY_CAMERA"
    checkpoint_update: str = "CHECKPOINT_UPDATE"
    color_change: str = "COLOR_CHANGE"


@dataclass(frozen=True)
class AppConfig:
    ros: RosConfig = field(default_factory=RosConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    gui: GuiConfig = field(default_factory=GuiConfig)
    command: CommandConfig = field(default_factory=CommandConfig)


CONFIG = AppConfig()
