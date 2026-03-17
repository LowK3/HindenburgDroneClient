from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal

class ConfirmWidget(QWidget):
    # Signals that gui.py can listen to
    accepted = Signal()
    rejected = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        confirm_layout = QVBoxLayout(self)
        confirm_layout.setAlignment(Qt.AlignCenter)
        
        confirm_panel = QWidget()
        confirm_panel.setStyleSheet("background-color: #1A1A1A; border: 2px solid #333; border-radius: 10px;")
        confirm_panel.setFixedSize(400, 150)
        
        panel_layout = QVBoxLayout(confirm_panel)
        panel_layout.setAlignment(Qt.AlignCenter)
        panel_layout.setSpacing(20)
        
        lbl = QLabel("DO YOU WANT TO SAVE THE CHANGES?")
        lbl.setStyleSheet("""
            font-family: 'Segoe Ui'; font-size: 18px; font-weight: bold; color: white; 
            border: none; background: transparent;
        """)
        lbl.setAlignment(Qt.AlignCenter)
        panel_layout.addWidget(lbl)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        self.btn_yes = QPushButton("YES")
        self.btn_yes.setFixedHeight(36)
        self.btn_yes.setStyleSheet("""
            QPushButton { 
                font-family: 'Segoe Ui'; background-color: #33FF33; color: black; 
                border: 2px solid #22CC22; border-radius: 5px; font-size: 18px; font-weight: bold; 
            }
            QPushButton:hover { background-color: #5EFF55; border: 2px solid #1D911C; }
        """)
        
        self.btn_no = QPushButton("NO")
        self.btn_no.setFixedHeight(36)
        self.btn_no.setStyleSheet("""
            QPushButton { 
                font-family: 'Segoe Ui'; background-color: #333; color: white; 
                border: 2px solid #444; border-radius: 5px; font-size: 18px; font-weight: bold; 
            }
            QPushButton:hover { background-color: #444444; border: 2px solid #666; }
        """)
        
        btn_layout.addWidget(self.btn_yes)
        btn_layout.addWidget(self.btn_no)
        panel_layout.addLayout(btn_layout)
        confirm_layout.addWidget(confirm_panel)

        self.btn_yes.clicked.connect(self.accepted.emit)
        self.btn_no.clicked.connect(self.rejected.emit)