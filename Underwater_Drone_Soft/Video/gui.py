import cv2, time
from PySide6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, 
    QWidget, QGridLayout, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap, QAction
from Video.overlay_manager import OverlayManager
from Control.input_manager import InputManager
from Video.connection_hud import ConnectionHud
from Utils.display_func import create_qpixmap
from Utils.common import log
from config import WINDOW_NAME, UDP_TIMEOUT
from Video.styles import (
    MAIN_PANEL_STYLE, CONNECTION_PANEL_STYLE, INFO_BTN_STYLE, ACCENT_GREEN, ACCENT_RED, 
    WAITING_TITLE, get_status_dot_style
)

class VideoWindow(QMainWindow):
    def __init__(self, frame_buffer, control_client):
        super().__init__()
        self.fb = frame_buffer
        self.is_true_fullscreen = False
        self.setWindowTitle(WINDOW_NAME)

        # 1. Setup Data & Timers
        self.input = InputManager(control_client, self.update_control_status)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)
        self.last_frame_time = time.time()

        # FPS counter
        self.fps_start_time = time.time()
        self.fps_frame_count = 0
        self.current_fps = 0

        # 2. Setup the User Interface
        self._setup_ui()
        self._create_actions()

        # 3. Final Window Config
        self.showMaximized()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        if self.input.settings.value("show_info_on_startup", True, type=bool):
            self.overlay.show_info_page()

    def _setup_ui(self):
        """ Builds the main video layouts and overlay stack. """
        #central = QWidget()
        #self.setCentralWidget(central)

        # Video container
        self.video_container = QWidget()
        self.setCentralWidget(self.video_container)
        self.video_layout = QGridLayout(self.video_container)
        self.video_layout.setContentsMargins(0, 0, 0, 0)

        # --- KAS ON VAJA???? ---
        #central.setLayout(QVBoxLayout())
        #central.layout().setContentsMargins(0, 0, 0, 0)
        #central.layout().addWidget(self.video_container)

        self.video_label = QLabel(alignment=Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: #0D0D0D;")
        self.video_layout.addWidget(self.video_label, 0, 0)

        # Waiting label
        self.waiting_label = QLabel("WAITING FOR STREAM...", alignment=Qt.AlignCenter)
        self.waiting_label.setStyleSheet(WAITING_TITLE)
        self.video_layout.addWidget(self.waiting_label, 0, 0, alignment=Qt.AlignCenter)

        # self.stack.addWidget(self.video_container)

        # Menu overlay setup
        self.overlay = OverlayManager(self)

        # Floating Info Button
        self.info_button = QPushButton("INFO")
        self.info_button.setFixedSize(90, 50)
        self.info_button.setStyleSheet(INFO_BTN_STYLE)
        self.video_layout.addWidget(self.info_button, 0, 0, alignment=Qt.AlignTop | Qt.AlignLeft)
        self.info_button.clicked.connect(self.overlay.show_info_page)

        # Connection Status Hud
        self.conn_panel = ConnectionHud()
        self.video_layout.addWidget(self.conn_panel, 0, 0, alignment=Qt.AlignTop | Qt.AlignRight)

    # --- INPUT EVENTS ---
    def keyPressEvent(self, event):
        self.input.key_pressed(event)

    def keyReleaseEvent(self, event):
        self.input.key_released(event)

    # --- WINDOW MANAGEMENT ---
    def resizeEvent(self, event):
        self.overlay.resize_overlays(self.rect())
        super().resizeEvent(event)

    # --- HUD STATUS UPDATES ---
    def update_video_status(self, connected):
        self.conn_panel.update_video_status(connected)

    def update_control_status(self, connected):
        self.conn_panel.update_control_status(connected)

    # --- VIDEO RENDERING ---
    def update_frame(self):
        if self.overlay.isVisible():
            return 

        with self.fb.lock:
            has_new = self.fb.new_frame
            frame = None if self.fb.frame is None else self.fb.frame.copy()
            self.fb.new_frame = False

        if has_new:
            self.last_frame_time = time.time()

        if frame is None:
            self.video_label.setPixmap(QPixmap())
            self.waiting_label.show()
            self.update_video_status(False)
            return

        if time.time() - self.last_frame_time > UDP_TIMEOUT:
            self.video_label.setPixmap(QPixmap())
            self.waiting_label.show()
            self.update_video_status(False)
            return

        if not has_new or frame is None:
            return

        self.waiting_label.hide()
        self.update_video_status(True)

        # FPS counter for testing
        self.fps_frame_count += 1
        elapsed_time = time.time() - self.fps_start_time

        if elapsed_time >= 1.0:
            self.current_fps = self.fps_frame_count / elapsed_time
            self.fps_frame_count = 0
            self.fps_start_time = time.time()

        fps_text = f"FPS: {int(self.current_fps)}"
        cv2.putText(frame, fps_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (50, 255, 50), 3)

        win_w = self.video_label.width()
        win_h = self.video_label.height()

        pixmap = create_qpixmap(frame, win_w, win_h)
        self.video_label.setPixmap(pixmap)

    # --- FULLSCREEN MANAGEMENT ---
    def _create_actions(self):
        self.action_toggle_fullscreen = QAction("Toggle Fullscreen", self)
        self.action_toggle_fullscreen.setShortcut("F11")
        self.action_toggle_fullscreen.triggered.connect(self.toggle_fullscreen)
        self.addAction(self.action_toggle_fullscreen)

        self.action_toggle_menu = QAction("Toggle Menu", self)
        self.action_toggle_menu.setShortcut("Esc")
        self.action_toggle_menu.triggered.connect(self.overlay.toggle_menu)
        self.addAction(self.action_toggle_menu)

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

