from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class GuiState:
    """State aktif GUI yang dikirim sebagai JSON lewat ROS2 std_msgs/String."""

    cmd: str = "READY"
    mode: str = "TRAINING"
    robot_status: str = "READY"
    kfs_color: str = "MERAH"
    selected_grid: Optional[int] = None
    selected_weapon_slot: Optional[int] = None
    selected_checkpoint: Optional[int] = None

    def to_packet(self) -> Dict[str, object]:
        packet: Dict[str, object] = {
            "source": "gui",
            "mode": self.mode,
            "cmd": self.cmd,
            "status": self.robot_status,
            "kfs_color": self.kfs_color,

            # Field compatibility untuk subscriber lama yang membaca key "color".
            "color": self.kfs_color,
        }

        if self.selected_grid is not None:
            packet["grid"] = self.selected_grid
        if self.selected_weapon_slot is not None:
            packet["weapon_slot"] = self.selected_weapon_slot
        if self.selected_checkpoint is not None:
            packet["checkpoint"] = self.selected_checkpoint

        return packet

    def build_packet(self, cmd: str, **payload: object) -> Dict[str, object]:
        self.cmd = cmd
        packet = self.to_packet()
        packet.update(payload)
        return packet

    def reset_decision(self) -> None:
        self.selected_grid = None
        self.selected_weapon_slot = None
        self.selected_checkpoint = None
        self.robot_status = "READY"
        self.cmd = "READY"
