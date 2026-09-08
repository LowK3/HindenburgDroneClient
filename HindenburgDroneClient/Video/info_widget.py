from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton
from PySide6.QtCore import Qt, Signal
from Video.styles import MAIN_PANEL_STYLE, TITLE_TEXT, TEXT, TEXT_BOLD, BTN_STYLE, CHECKBOX_STYLE

class InfoWidget(QWidget):
    close_clicked = Signal()
    tutorial_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignCenter)
        
        self.panel = QWidget()
        self.panel.setObjectName("InfoPanel")
        self.panel.setStyleSheet(MAIN_PANEL_STYLE)
        self.panel.setFixedWidth(500)
        
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setAlignment(Qt.AlignCenter)
        panel_layout.setContentsMargins(30, 30, 30, 30)
        panel_layout.setSpacing(15)
        
        title = QLabel("INSTRUCTIONS")
        title.setStyleSheet(TITLE_TEXT)
        title.setAlignment(Qt.AlignCenter)
        panel_layout.addWidget(title)
        
        welcome = QLabel("Welcome to the Hindenburg Drone Controller!")
        welcome.setStyleSheet(TEXT_BOLD)
        panel_layout.addWidget(welcome)

        instructions = QLabel(
            "Default Controls:\n"
            "- Drive: W, A, S, D\n"
            "- Tilt: E (Up) and Q (Down)\n"
            "- Front Power: I (Increase) and K (Decrease)\n"
            "- Rear Power: O (Increase) and L (Decrease)\n\n"
            "Press 'Esc' to open the menu and configure custom keybindings in the Settings tab.\n\n"
            "Important: Ensure the drone is fully powered on and connected to the Server before driving."
        )
        instructions.setWordWrap(True)
        instructions.setMinimumHeight(250)
        instructions.setStyleSheet(TEXT)
        panel_layout.addWidget(instructions)
        
        self.dont_show_cb = QCheckBox("Don't show this automatically on startup")
        self.dont_show_cb.setStyleSheet(CHECKBOX_STYLE)
        panel_layout.addWidget(self.dont_show_cb)
        panel_layout.addSpacing(20)

        self.tutorial_btn = QPushButton("CONNECTION TUTORIAL")
        self.tutorial_btn.setFixedHeight(50)
        self.tutorial_btn.setStyleSheet(BTN_STYLE)
        panel_layout.addWidget(self.tutorial_btn)
        
        self.close_btn = QPushButton("CLOSE")
        self.close_btn.setFixedHeight(50)
        self.close_btn.setStyleSheet(BTN_STYLE)
        panel_layout.addWidget(self.close_btn)
        
        outer_layout.addWidget(self.panel)

        self.close_btn.clicked.connect(self.close_clicked.emit)
        self.tutorial_btn.clicked.connect(self.tutorial_clicked.emit)