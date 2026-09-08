from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from Video.styles import MAIN_PANEL_STYLE, TITLE_2_TEXT, BTN_STYLE, GREEN_BTN_STYLE

class ConfirmWidget(QWidget):
    accepted = Signal()
    rejected = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        confirm_layout = QVBoxLayout(self)
        confirm_layout.setAlignment(Qt.AlignCenter)
        
        confirm_panel = QWidget()
        confirm_panel.setObjectName("ConfirmPanel")
        confirm_panel.setStyleSheet(MAIN_PANEL_STYLE)
        confirm_panel.setFixedSize(420, 160)
        
        panel_layout = QVBoxLayout(confirm_panel)
        panel_layout.setAlignment(Qt.AlignCenter)
        panel_layout.setSpacing(20)
        
        lbl = QLabel("DO YOU WANT TO SAVE THE CHANGES?")
        lbl.setStyleSheet(TITLE_2_TEXT)
        lbl.setAlignment(Qt.AlignCenter)
        panel_layout.addWidget(lbl)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        self.btn_yes = QPushButton("YES")
        self.btn_yes.setFixedHeight(36)
        self.btn_yes.setStyleSheet(GREEN_BTN_STYLE)
        
        self.btn_no = QPushButton("NO")
        self.btn_no.setFixedHeight(36)
        self.btn_no.setStyleSheet(BTN_STYLE)
        
        btn_layout.addWidget(self.btn_yes)
        btn_layout.addWidget(self.btn_no)
        panel_layout.addLayout(btn_layout)
        confirm_layout.addWidget(confirm_panel)

        self.btn_yes.clicked.connect(self.accepted.emit)
        self.btn_no.clicked.connect(self.rejected.emit)