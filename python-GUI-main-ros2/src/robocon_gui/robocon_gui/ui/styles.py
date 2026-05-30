"""Stylesheet Robocon GUI.

Tema ini dibuat supaya Page 1 dan Page 2 lebih dekat ke visual matte-dark
bernuansa Kali wallpaper: gelap, biru baja, tidak terlalu neon, tetapi warna
toggle penting tetap jelas.
"""


def global_styles() -> str:
    return """
    QMainWindow {
        background: #070b12;
        color: #e6edf6;
    }
    QWidget {
        color: #e6edf6;
        font-family: Inter, Segoe UI, Arial, sans-serif;
        font-size: 13px;
    }
    QFrame#Card {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #111c2a, stop:1 #0b1320);
        border: 1px solid #1f3048;
        border-radius: 16px;
    }
    QFrame#SoftCard {
        background: #0b1320;
        border: 1px solid #22344e;
        border-radius: 14px;
    }
    QLabel#TitleBar {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #152238, stop:1 #111b2d);
        color: #e6edf6;
        border: 1px solid #2a3e5a;
        border-radius: 14px;
        padding: 10px 18px;
        font-size: 18px;
        font-weight: 850;
        letter-spacing: 0.6px;
    }
    QLabel#SectionTitle {
        color: #6fa7df;
        font-size: 13px;
        font-weight: 850;
        padding: 4px 8px;
        letter-spacing: 0.4px;
    }
    QPlainTextEdit {
        background: #050a12;
        border: 1px solid #263850;
        border-radius: 12px;
        color: #79b8ff;
        selection-background-color: #1f5fa8;
        font-family: JetBrains Mono, Consolas, monospace;
        font-size: 12px;
        padding: 10px;
    }
    QScrollBar:vertical {
        background: #08111d;
        width: 11px;
        margin: 8px 2px 8px 2px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background: #30445f;
        border-radius: 5px;
        min-height: 30px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    """


def status_style(color: str = "#0f8a83") -> str:
    return f"""
    QLabel {{
        background: {color};
        color: #f8fafc;
        border: 1px solid rgba(255,255,255,0.16);
        border-radius: 12px;
        padding: 12px;
        font-size: 15px;
        font-weight: 850;
    }}
    """


def nav_button(active: bool = False) -> str:
    if active:
        bg = "#1f5fa8"
        border = "#3e91f6"
        color = "#eaf4ff"
    else:
        bg = "#0b1320"
        border = "#243751"
        color = "#8fa3bd"
    return f"""
    QPushButton {{
        background: {bg};
        color: {color};
        border: 2px solid {border};
        border-radius: 16px;
        font-size: 18px;
        font-weight: 850;
        min-height: 42px;
        min-width: 74px;
    }}
    QPushButton:hover {{
        background: #183457;
        border-color: #4d8ed8;
        color: #f4f8ff;
    }}
    """


def grid_button(active: bool = False) -> str:
    if active:
        return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #1e436f, stop:1 #1f5fa8);
            color: #edf6ff;
            border: 3px solid #3e91f6;
            border-radius: 6px;
            font-size: 32px;
            font-weight: 900;
        }
        QPushButton:hover { background: #255f9f; }
        """
    return """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #172536, stop:1 #101b2b);
        color: #e2e8f0;
        border: 2px solid #263850;
        border-radius: 6px;
        font-size: 32px;
        font-weight: 900;
    }
    QPushButton:hover {
        background: #1b3048;
        border-color: #4d8ed8;
    }
    """


def weapon_button(active: bool = False) -> str:
    bg = "#f1f5f9" if not active else "#f6c343"
    border = "#cbd5e1" if not active else "#ffd25f"
    color = "#0f172a"
    return f"""
    QPushButton {{
        background: {bg};
        color: {color};
        border: 2px solid {border};
        border-radius: 14px;
        font-size: 20px;
        font-weight: 850;
        min-height: 72px;
    }}
    QPushButton:hover {{
        background: #dbeafe;
        border-color: #93c5fd;
    }}
    """


def box_button(color: str, active: bool = False) -> str:
    if color == "red":
        bg = "#c92f2f" if active else "#9f2424"
        border = "#ef5350" if active else "#cb3835"
    else:
        bg = "#1c55a3" if active else "#0f3477"
        border = "#3d83d7" if active else "#1f5fa8"
    return f"""
    QPushButton {{
        background: {bg};
        color: #f8fafc;
        border: 3px solid {border};
        border-radius: 14px;
        font-size: 18px;
        font-weight: 850;
        min-height: 150px;
    }}
    QPushButton:hover {{
        border-color: #f1f5f9;
    }}
    """


def checkpoint_button(active: bool = False) -> str:
    bg = "#0f8a83" if active else "#0c6863"
    border = "#33bdb5" if active else "#167f78"
    return f"""
    QPushButton {{
        background: {bg};
        color: #ecfeff;
        border: 3px solid {border};
        border-radius: 14px;
        font-size: 18px;
        font-weight: 850;
        min-height: 150px;
    }}
    QPushButton:hover {{
        background: #109c93;
        border-color: #5eead4;
    }}
    """


def action_button(kind: str, active: bool = False) -> str:
    palette = {
        "start": ("#0d756f", "#f8fafc", "#20a59c"),
        "stop": ("#c73333", "#f8fafc", "#ef5350"),
        "reset": ("#f4c542", "#0f172a", "#f8d96a"),
        "camera_reset": ("#f4c542", "#0f172a", "#f8d96a"),
        "camera_stop": ("#8f2323", "#f8fafc", "#ef5350"),
    }
    bg, color, border = palette.get(kind, ("#172536", "#e6edf6", "#2b3e59"))
    return f"""
    QPushButton {{
        background: {bg};
        color: {color};
        border: 2px solid {border};
        border-radius: 14px;
        padding: 12px 18px;
        font-size: 18px;
        font-weight: 850;
        min-height: 78px;
    }}
    QPushButton:hover {{
        border-color: #f1f5f9;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {bg}, stop:1 #1f3048);
    }}
    """


def panel_header() -> str:
    return """
    QLabel {
        background: #142033;
        color: #b8c6d9;
        border: 1px solid #263850;
        border-radius: 12px;
        padding: 4px 16px;
        font-size: 18px;
        font-weight: 850;
    }
    """
