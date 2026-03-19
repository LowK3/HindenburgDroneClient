from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from Video.styles import MAIN_PANEL_STYLE, TITLE_TEXT, MENU_BTN_STYLE

class MainMenuWidget(QWidget):
    resume_clicked = Signal()
    settings_clicked = Signal()
    quit_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_outer_layout = QVBoxLayout(self)
        main_outer_layout.setAlignment(Qt.AlignCenter)

        menu_panel = QWidget()
        menu_panel.setObjectName("MainPanel")
        menu_panel.setStyleSheet(MAIN_PANEL_STYLE)
        menu_panel.setFixedWidth(350)

        menu_layout = QVBoxLayout(menu_panel)
        menu_layout.setAlignment(Qt.AlignCenter)
        menu_layout.setSpacing(20)
        menu_layout.setContentsMargins(40, 40, 40, 40) 

        title = QLabel("MAIN MENU")
        title.setStyleSheet(TITLE_TEXT)
        title.setAlignment(Qt.AlignCenter)
        menu_layout.addWidget(title)

        self.resume_btn = QPushButton("RESUME")
        self.settings_btn = QPushButton("SETTINGS")
        self.quit_btn = QPushButton("QUIT")

        for btn in (self.resume_btn, self.settings_btn, self.quit_btn):
            btn.setFixedHeight(50)
            btn.setFixedWidth(200)
            btn.setStyleSheet(MENU_BTN_STYLE)
            menu_layout.addWidget(btn)

        main_outer_layout.addWidget(menu_panel)

        # Connect button clicks to the signals
        self.resume_btn.clicked.connect(self.resume_clicked.emit)
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        self.quit_btn.clicked.connect(self.quit_clicked.emit)