from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QDialog,
    QPushButton, QVBoxLayout, QWidget, QGridLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
import sys
import cv2

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Menu")
        self.setModal(True)

        layout = QVBoxLayout()
        resume = QPushButton("Resume")
        quit_ = QPushButton("Quit")

        resume.clicked.connect(self.accept)
        quit_.clicked.connect(lambda: QApplication.quit())

        layout.addWidget(resume)
        layout.addWidget(quit_)
        self.setLayout(layout)

class VideoWindow(QMainWindow):
    def __init__(self, frame_buffer):
        super().__init__()
        self.fb = frame_buffer

        self.video_label = QLabel(alignment=Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")  # always keep video area black when empty

        self.overlay = QLabel("Waiting for stream...", alignment=Qt.AlignCenter)
        self.overlay.setStyleSheet(
            "background-color: transparent; color: white; font-size: 24pt;"
        )
        # Allow clicks to pass through overlay to underlying widgets (not strictly necessary here)
        self.overlay.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Container that overlays the two labels in the same grid cell
        container = QWidget()
        grid = QGridLayout(container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.addWidget(self.video_label, 0, 0)
        grid.addWidget(self.overlay, 0, 0, alignment=Qt.AlignCenter)

        self.setCentralWidget(container)

        self.setWindowTitle("Submarine Stream")
        self.showNormal()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)  # ~60 FPS

    def update_frame(self):
        with self.fb.lock:
            frame = None if self.fb.frame is None else self.fb.frame.copy()

        if frame is None:
            self.video_label.setPixmap(QPixmap())
            self.overlay.setText("Waiting for stream...")
            self.overlay.show()
            return

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            SettingsDialog(self).exec()
