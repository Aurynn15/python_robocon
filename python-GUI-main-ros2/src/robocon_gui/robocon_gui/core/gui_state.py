from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class GuiState:
    """State aktif GUI yang dikonversi menjadi JSON untuk ROS1 std_msgs/String."""

    cmd: str = "READY"
    color_mode: str = "MERAH"
    robot_status: str = "READY"
    checkpoint_active: List[bool] = field(default_factory=lambda: [False] * 12)

    def selected_checkpoints(self) -> List[int]:
        """Mengubah boolean CP menjadi nomor checkpoint aktif: [1, 2, 3]."""
        return [idx + 1 for idx, active in enumerate(self.checkpoint_active) if active]

    def to_packet(self) -> Dict[str, object]:
        """Bentuk payload command yang akan dikirim ke robot lewat topic ROS1."""
        return {
            "cmd": self.cmd,
            "color": self.color_mode,
            "checkpoints": self.selected_checkpoints(),
            "status": self.robot_status,
        }

    def reset_checkpoints(self) -> None:
        self.checkpoint_active = [False] * 12
