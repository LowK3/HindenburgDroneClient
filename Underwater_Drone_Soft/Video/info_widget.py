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
            "- Use the W, A, S, D keys to drive the drone.\n"
            "- Use U and J to tilt the drone up and down.\n"
            "- Press 'Esc' to pause the stream and open the menu.\n"
            "- You can change your keybindings in the Settings menu.\n\n"
            "Ensure the drone is powered on and connected to the network before driving."
        )
        instructions.setWordWrap(True)
        instructions.setMinimumHeight(200)
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