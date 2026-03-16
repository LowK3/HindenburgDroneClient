from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import os

class TutorialWidget(QWidget):
    """ The scrollable connection tutorial page. """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignCenter)

        self.panel = QWidget()
        self.panel.setObjectName("TutorialPanel")
        self.panel.setStyleSheet("#TutorialPanel { background-color: #1A1A1A; border-radius: 15px; border: 2px solid #333; }")
        self.panel.setFixedSize(900, 750)
        
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(30, 30, 30, 30)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea { 
                border: none; background: transparent; 
            }
            QScrollBar:vertical {
                border: none; background: transparent; width: 10px; margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #333; min-height: 25px; border: 1px solid #444; 
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #444444; border: 1px solid #666;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none; background: none; height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)

        title = QLabel("CONNECTION TUTORIAL")
        title.setStyleSheet("font-family: 'Segoe Ui'; font-size: 28px; font-weight: bold; color: white;")
        title.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(title)

        steps = [
            ("1. POWER ON", "Plug the power bank into the Raspberry Pi to start the drone."),
            ("2. CONNECT ETHERNET CABLE", "Connect the drone to your computer via the Ethernet cable."),
            ("3. OPEN PuTTY", "Connect to the Raspberry Pi using PuTTY and an SSH link. (Host Name: server)"),
            ("4. START THE SERVER", "Start the server on the drone using the PuTTY terminal. Navigate to the "
             "Server repository and start the server using\n'python3 main_server'.\n"
             "(Note: In the future, the server will start automatically when Raspberry is powered on)."),
            ("5. CONNECT", "Turn on the Hindenburg Windows app. The connection between the drone and "
             "server will be established automatically."),
            ("6. READY TO DIVE", "Check the top right indicators. If VIDEO and CONTROL are green, you are ready to drive!"),
            ("TROUBLE CONNECTING?", "If you have trouble connecting, you can see the log files in the "
             "Documents folder on your computer and the server logs from the PuTTY in the Linux home folder.")
        ]
        
        for i, (step_title, step_text) in enumerate(steps):
            st_lbl = QLabel(step_title)
            st_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
            scroll_layout.addWidget(st_lbl)

            desc_lbl = QLabel(step_text)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet("font-size: 15px; color: white;")
            scroll_layout.addWidget(desc_lbl)
            
            if i < len(steps) - 1:
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

            if i < len(steps) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setStyleSheet("background-color: #333;")
                scroll_layout.addWidget(line)

        scroll_area.setWidget(scroll_content)
        panel_layout.addWidget(scroll_area)

        panel_layout.addSpacing(30)
        self.back_btn = QPushButton("BACK")
        self.back_btn.setFixedHeight(50)
        self.back_btn.setStyleSheet("""
            QPushButton {
                font-family: 'Segoe Ui'; background-color: #333; color: white;
                border: 2px solid #444; border-radius: 5px;
                font-size: 18px; font-weight: bold; margin-top: 10px;
            }
            QPushButton:hover { background-color: #444444; border: 2px solid #666; }
        """)
        panel_layout.addWidget(self.back_btn)
        
        outer_layout.addWidget(self.panel)