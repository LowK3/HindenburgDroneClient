from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QDialog,
    QPushButton, QVBoxLayout, QWidget, QGridLayout,
    QMenu, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap, QAction
from PySide6.QtWidgets import QStackedLayout
from PySide6.QtWidgets import QGraphicsBlurEffect
import sys
import cv2

class VideoWindow(QMainWindow):
    def __init__(self, frame_buffer):
        super().__init__()
        self.fb = frame_buffer
        self.is_true_fullscreen = False

        self.setWindowTitle("Submarine Stream")

        # ---- Central widget ----
        central = QWidget()
        self.setCentralWidget(central)

        self.stack = QStackedLayout(central)
        self.stack.setContentsMargins(0, 0, 0, 0)

        # ---- Video label ----
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

        # ---- Menu overlay ----
        self.menu_overlay = self.create_overlay()
        self.stack.addWidget(self.menu_overlay)
        self.menu_overlay.hide()

        # Default windowed fullscreen
        self.showMaximized()

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)

        self._create_actions()
        

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
        overlay = QWidget()
        overlay.setStyleSheet("background-color: rgba(0,0,0,150);")

        layout = QVBoxLayout(overlay)
        layout.setAlignment(Qt.AlignCenter)

        resume_btn = QPushButton("Resume")
        settings_btn = QPushButton("Settings")
        quit_btn = QPushButton("Quit")

        for btn in (resume_btn, settings_btn, quit_btn):
            btn.setFixedWidth(250)
            btn.setFixedHeight(50)

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
            self.video_label.setGraphicsEffect(None)
            self.menu_overlay.hide()
        else:
            blur = QGraphicsBlurEffect()
            blur.setBlurRadius(25)
            self.video_label.setGraphicsEffect(blur)
            self.menu_overlay.show()

    def update_frame(self):
        with self.fb.lock:
            frame = None if self.fb.frame is None else self.fb.frame.copy()

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

        frame_resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

        qt_img = QImage(frame_resized.data, new_w, new_h, 3 * new_w, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(qt_img)

        self.video_label.setPixmap(pixmap)
        self.overlay.hide()
