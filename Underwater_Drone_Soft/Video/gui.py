import sys,cv2
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QDialog,
    QPushButton, QVBoxLayout, QWidget, QGridLayout,
    QMenu, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap, QAction
from PySide6.QtWidgets import QStackedLayout
from PySide6.QtWidgets import QGraphicsBlurEffect
from config import WINDOW_NAME

class VideoWindow(QMainWindow):
    def __init__(self, frame_buffer, control_client):
        super().__init__()
        self.fb = frame_buffer

        self.control = control_client
        self.current_command = "STOP\n"

        self.setWindowTitle(WINDOW_NAME)
        self.is_true_fullscreen = False

        # Heartbeat timer
        self.control_timer = QTimer()
        self.control_timer.timeout.connect(self.send_control)
        self.control_timer.start(100)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        self.stack = QStackedLayout(central)
        self.stack.setContentsMargins(0, 0, 0, 0)

        # Video label
        self.video_label = QLabel(alignment=Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")

        self.video_container = QWidget()
        self.video_layout = QGridLayout(self.video_container)
        self.video_layout.setContentsMargins(0, 0, 0, 0)

        self.video_layout.addWidget(self.video_label, 0, 0)

        # Waiting label
        self.waiting_label = QLabel("Waiting for stream...", alignment=Qt.AlignCenter)
        self.waiting_label.setStyleSheet("""
            color: white;
            font-size: 28px;
            background-color: transparent;
        """)
        self.video_layout.addWidget(self.waiting_label, 0, 0, alignment=Qt.AlignCenter)

        # Replace stack base widget
        self.stack.addWidget(self.video_container)

        # Menu overlay
        self.menu_overlay = self.create_overlay()
        self.menu_overlay.setParent(self.centralWidget()) # Put it on top
        self.menu_overlay.setGeometry(self.rect()) # Make it cover the screen
        self.menu_overlay.hide()

        # Default windowed fullscreen
        self.showMaximized()

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(32)

        self._create_actions()

    def send_control(self):
        """ Sends the continuous heartbeat to the drone """

        if self.control and self.control.sock:
            self.control.send(self.current_command)

    def keyPressEvent(self, event):
        if event.isAutoRepeat(): 
            return
        key = event.key()

        # 1. Continuous Movement (Updates the heartbeat)
        if key == Qt.Key_W: self.current_command = "W\n"
        elif key == Qt.Key_S: self.current_command = "S\n"
        elif key == Qt.Key_A: self.current_command = "A\n"
        elif key == Qt.Key_D: self.current_command = "D\n"
        elif key == Qt.Key_U: self.current_command = "UP\n"
        elif key == Qt.Key_J: self.current_command = "DOWN\n"

        # 2. Discrete Adjustments (Sent instantly, once per press)
        elif key == Qt.Key_O: self.control.send("REAR+\n")
        elif key == Qt.Key_L: self.control.send("REAR-\n")
        elif key == Qt.Key_I: self.control.send("FRONT+\n")
        elif key == Qt.Key_K: self.control.send("FRONT-\n")

        elif key == Qt.Key_Escape:
            self.toggle_overlay()

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat(): 
            return
            
        # Only stop the drone if a movement key was released
        movement_keys = {Qt.Key_W, Qt.Key_S, Qt.Key_A, Qt.Key_D, Qt.Key_U, Qt.Key_J}
        if event.key() in movement_keys:
            self.current_command = "STOP\n"

    def _create_actions(self):
        self.action_toggle_fullscreen = QAction("Toggle Fullscreen", self)
        self.action_toggle_fullscreen.setShortcut("F11")
        self.action_toggle_fullscreen.triggered.connect(self.toggle_fullscreen)
        self.addAction(self.action_toggle_fullscreen)

    def show_windowed_fullscreen(self):
        self.is_true_fullscreen = False
        self.showMaximized()

    def show_true_fullscreen(self):
        self.is_true_fullscreen = True
        self.showFullScreen()

    def toggle_fullscreen(self):
        if self.is_true_fullscreen:
            self.show_windowed_fullscreen()
        else:
            self.show_true_fullscreen()

    def create_overlay(self):
        overlay = QWidget(self.centralWidget())
        # Dark grey semi-transparent background (RGBA: 40, 40, 40, 180)
        overlay.setStyleSheet("background-color: rgba(40, 40, 40, 180);")

        layout = QVBoxLayout(overlay)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Common style for dark buttons
        button_style = """
            QPushButton {
                background-color: #1A1A1A;
                color: white;
                border: 1px solid #333;
                border-radius: 5px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333333;
                border: 1px solid #555;
            }
            QPushButton:pressed {
                background-color: #000000;
            }
        """

        resume_btn = QPushButton("Resume")
        settings_btn = QPushButton("Settings")
        quit_btn = QPushButton("Quit")

        for btn in (resume_btn, settings_btn, quit_btn):
            btn.setFixedWidth(250)
            btn.setFixedHeight(50)
            btn.setStyleSheet(button_style)

        resume_btn.clicked.connect(self.toggle_overlay)
        quit_btn.clicked.connect(self.close)

        layout.addWidget(resume_btn)
        layout.addWidget(settings_btn)
        layout.addWidget(quit_btn)

        return overlay

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.toggle_overlay()
    
    def toggle_overlay(self):
        if self.menu_overlay.isVisible():
            # Remove effect and hide
            self.video_label.setGraphicsEffect(None)
            self.menu_overlay.hide()
        else:
            # 1. Apply heavy blur to the video label
            blur = QGraphicsBlurEffect()
            blur.setBlurRadius(40) # Increased radius for "grey wash" look
            self.video_label.setGraphicsEffect(blur)
        
            # 2. Ensure overlay covers the whole window and show
            self.menu_overlay.setGeometry(self.centralWidget().rect())
            self.menu_overlay.show()
            self.menu_overlay.raise_() # Make sure it's on top of everything

    def resizeEvent(self, event):
    # Ensure the menu stays full-screen even when window is resized
        self.menu_overlay.setGeometry(self.rect())
        super().resizeEvent(event)

    def update_frame(self):
        if self.menu_overlay.isVisible():
            return 

        with self.fb.lock:
            if not self.fb.new_frame:
                return
        
            frame = None if self.fb.frame is None else self.fb.frame.copy()
            self.fb.new_frame = False

        if frame is None:
            self.video_label.setPixmap(QPixmap())
            self.waiting_label.show()
            return

        self.waiting_label.hide()

        win_w = self.video_label.width()
        win_h = self.video_label.height()

        frame_h, frame_w, _ = frame.shape
        scale = min(win_w / frame_w, win_h / frame_h)
        new_w = int(frame_w * scale)
        new_h = int(frame_h * scale)

        frame_resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        frame_resized = frame_resized[:, :, ::-1].copy()

        qt_img = QImage(frame_resized.data, new_w, new_h, 3 * new_w, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_img))
