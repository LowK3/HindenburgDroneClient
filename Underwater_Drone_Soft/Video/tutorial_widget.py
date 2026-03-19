import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from Video.styles import (
    MAIN_PANEL_STYLE, TITLE_TEXT, TITLE_2_TEXT, TEXT, BTN_STYLE, 
    SCROLL_AREA_STYLE, BTN_BG_COLOR
)

class TutorialWidget(QWidget):
    back_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignCenter)

        self.panel = QWidget()
        self.panel.setObjectName("TutorialPanel")
        self.panel.setStyleSheet(MAIN_PANEL_STYLE)
        self.panel.setFixedSize(900, 750)
        
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(30, 30, 30, 30)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(SCROLL_AREA_STYLE)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)

        title = QLabel("CONNECTION TUTORIAL")
        title.setStyleSheet(TITLE_TEXT)
        title.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(title)

        steps = [
            ("1. POWER ON", "Plug the power bank into the Raspberry Pi to start the drone."),
            ("2. CONNECT ETHERNET CABLE", "Connect the drone to your computer via the Ethernet cable."),
            ("3. OPEN PuTTY", "Establish an SSH connection to the Raspberry Pi using PuTTY (Host Name: server)."),
            ("4. START THE SERVER", "In the PuTTY terminal, navigate to the server repository and run:\n"
             "  'python3 main_server.py'\n\n"
             "(Note: In the future, the server will start automatically when Raspberry is powered on)."),
            ("5. CONNECT", "Launch the Hindenburg Windows application. The connection between the drone and "
             "server will be established automatically."),
            ("6. READY TO DIVE", "Check the status indicators in the top right. When VIDEO and CONTROL turn green, you are ready to dive!"),
            ("TROUBLE CONNECTING?", "If you have trouble connecting, or run into any issues, check the Logs for errors."),
            ("App Logs", "Click the 'LOGS' button in the Main Menu to instantly view your client side logs or navigate to the main folder of the App."),
            ("Server Logs", "Open PuTTY and navigate to the main folder of the Server to open and check the Log file on the Raspberry Pi.")
        ]
        
        for i, (step_title, step_text) in enumerate(steps):
            st_lbl = QLabel(step_title)
            st_lbl.setStyleSheet(TITLE_2_TEXT)
            scroll_layout.addWidget(st_lbl)

            desc_lbl = QLabel(step_text)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(TEXT)
            scroll_layout.addWidget(desc_lbl)
            
            if i < len(steps) - 3:
                img_label = QLabel()
                img_label.setAlignment(Qt.AlignCenter)
                img_label.setFixedHeight(400)
            
                img_path = os.path.join("Video", "assets", f"{i+1}.jpg")
            
                if os.path.exists(img_path):
                    pixmap = QPixmap(img_path)
                    scaled_pixmap = pixmap.scaled(800, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    img_label.setPixmap(scaled_pixmap)
                else:
                    img_label.setText(f"Image Missing: {img_path}")
                    img_label.setStyleSheet("color: red; border: 1px solid red;")
            
                scroll_layout.addWidget(img_label)

            if i < len(steps) - 3:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setStyleSheet(f"background-color: {BTN_BG_COLOR}")
                scroll_layout.addWidget(line)

        scroll_area.setWidget(scroll_content)
        panel_layout.addWidget(scroll_area)

        panel_layout.addSpacing(40)
        self.back_btn = QPushButton("BACK")
        self.back_btn.setFixedHeight(50)
        self.back_btn.setStyleSheet(BTN_STYLE)
        panel_layout.addWidget(self.back_btn)
        
        outer_layout.addWidget(self.panel)

        self.back_btn.clicked.connect(self.back_clicked.emit)