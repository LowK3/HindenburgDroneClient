from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from Video.styles import CONNECTION_PANEL_STYLE, ACCENT_RED, get_status_dot_style

class ConnectionHud(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(CONNECTION_PANEL_STYLE)
        
        conn_layout = QHBoxLayout(self)
        conn_layout.setContentsMargins(20, 7, 20, 7)
        conn_layout.setSpacing(5)

        self.vid_dot = QLabel()
        self.vid_dot.setFixedSize(12, 12)
        self.vid_dot.setObjectName("StatusDot")
        self.vid_dot.setStyleSheet(f"background-color: {ACCENT_RED};") 
        self.vid_text = QLabel("VIDEO")

        conn_layout.addWidget(self.vid_dot)
        conn_layout.addWidget(self.vid_text)
        conn_layout.addSpacing(25)

        self.ctrl_dot = QLabel()
        self.ctrl_dot.setObjectName("StatusDot")
        self.ctrl_dot.setStyleSheet(f"background-color: {ACCENT_RED};") 
        self.ctrl_text = QLabel("CONTROL")

        conn_layout.addWidget(self.ctrl_dot)
        conn_layout.addWidget(self.ctrl_text)

    def update_video_status(self, connected: bool):
        self.vid_dot.setStyleSheet(get_status_dot_style(connected))

    def update_control_status(self, connected: bool):
        self.ctrl_dot.setStyleSheet(get_status_dot_style(connected))