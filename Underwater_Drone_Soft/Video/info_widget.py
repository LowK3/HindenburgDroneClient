from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton
from PySide6.QtCore import Qt

class InfoWidget(QWidget):
    """ The info page with instructions. """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignCenter)
        
        self.panel = QWidget()
        self.panel.setObjectName("SolidPanel")
        self.panel.setStyleSheet("#SolidPanel { background-color: #1A1A1A; border-radius: 15px; border: 2px solid #333; }")
        self.panel.setFixedWidth(500)
        
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setAlignment(Qt.AlignCenter)
        panel_layout.setContentsMargins(30, 30, 30, 30)
        panel_layout.setSpacing(15)
        
        title = QLabel("INSTRUCTIONS")
        title.setStyleSheet("""
            font-family: 'Segoe Ui'; font-size: 32px; font-weight: bold; 
            color: white; background: transparent;
        """)
        title.setAlignment(Qt.AlignCenter)
        panel_layout.addWidget(title)
        
        welcome = QLabel("Welcome to the Hindenburg Drone Controller!")
        welcome.setStyleSheet("""
            font-family: 'Segoe Ui'; font-size: 16px; font-weight: bold; 
            color: white; background: transparent;
        """)
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
        instructions.setStyleSheet("""
            font-family: 'Segoe Ui'; font-size: 16px; color: white; 
            background: transparent;
        """)
        panel_layout.addWidget(instructions)
        
        self.dont_show_cb = QCheckBox("Don't show this automatically on startup")
        self.dont_show_cb.setStyleSheet("""
            QCheckBox { color: white; font-size: 14px; background: transparent; }
            QCheckBox::indicator { border: 2px solid #444; border-radius: 5px; width: 16px; height: 16px; }
            QCheckBox::indicator:checked { background-color: white; border-radius: 5px;}
        """)
        panel_layout.addWidget(self.dont_show_cb)
        
        self.close_btn = QPushButton("CLOSE")
        self.close_btn.setFixedHeight(50)
        self.close_btn.setStyleSheet("""
            QPushButton {
                font-family: 'Segoe Ui'; background-color: #333; color: white;
                border: 2px solid #444; border-radius: 5px;
                font-size: 18px; font-weight: bold; margin-top: 15px;
            }
            QPushButton:hover { background-color: #444444; border: 2px solid #666; }
        """)
        panel_layout.addWidget(self.close_btn)
        
        outer_layout.addWidget(self.panel)