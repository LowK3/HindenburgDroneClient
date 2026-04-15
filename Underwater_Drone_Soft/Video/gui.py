import cv2
import time
from PySide6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, 
    QWidget, QGridLayout, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap, QAction
from Video.overlay_manager import OverlayManager
from Control.input_manager import InputManager
from Video.connection_hud import ConnectionHud
from Video.telemetry_widget import LeftTelemetryWidget, RightTelemetryWidget, WarningWidget
from Utils.display_func import create_qpixmap
from Utils.logger import log
from config import WINDOW_NAME, UDP_TIMEOUT, GUI_REFRESH_RATE
from Video.styles import (
    MAIN_PANEL_STYLE, CONNECTION_PANEL_STYLE, INFO_BTN_STYLE, ACCENT_GREEN, ACCENT_RED, 
    WAITING_TITLE, get_status_dot_style
)

class VideoWindow(QMainWindow):
    def __init__(self, frame_buffer, control_client):
        super().__init__()
        self.fb = frame_buffer
        self.control = control_client
        self.setWindowTitle(WINDOW_NAME)

        # 1. Setup Data & Timers
        self.input = InputManager()
        self.input.command_requested.connect(self.control.send)

        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        self.timer.start(GUI_REFRESH_RATE)
        self.last_frame_time = time.time()

        # 2. Setup the User Interface
        self._setup_ui()
        self._create_actions()

        # 3. Final Window Config
        self.showMaximized()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        if self.input.settings.value("show_info_on_startup", True, type=bool):
            self.overlay.show_info_page()

        # Update telemetry
        self.control.telemetry_received.connect(self.left_telemetry_panel.update_ui)
        self.control.telemetry_received.connect(self.right_telemetry_panel.update_ui)
        self.control.telemetry_received.connect(self.warning_panel.update_ui)


    def _setup_ui(self):
        """ Builds the main video layouts and overlay stack. """
        central = QWidget()
        self.setCentralWidget(central)

        # Video container
        self.video_container = QWidget()
        self.video_layout = QGridLayout(self.video_container)
        self.video_layout.setContentsMargins(0, 0, 0, 0)

        # Make the video container fill the entire window
        central.setLayout(QVBoxLayout())
        central.layout().setContentsMargins(0, 0, 0, 0)
        central.layout().addWidget(self.video_container)

        self.video_label = QLabel(alignment=Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: #0D0D0D;")
        self.video_layout.addWidget(self.video_label, 0, 0)

        # Waiting label
        self.waiting_label = QLabel("WAITING FOR STREAM...", alignment=Qt.AlignCenter)
        self.waiting_label.setStyleSheet(WAITING_TITLE)
        self.video_layout.addWidget(self.waiting_label, 0, 0, alignment=Qt.AlignCenter)

        self.overlay = OverlayManager(self)

        # Top-left container for info button and telemetry
        self.top_left_container = QWidget()
        tl_layout = QVBoxLayout(self.top_left_container)
        tl_layout.setContentsMargins(10, 10, 0, 10)
        tl_layout.setSpacing(20)

        self.info_button = QPushButton("INFO")
        self.info_button.setFixedSize(90, 50)
        self.info_button.setStyleSheet(INFO_BTN_STYLE)
        tl_layout.addWidget(self.info_button, alignment=Qt.AlignTop | Qt.AlignLeft)
        self.info_button.clicked.connect(self._open_info_page_safely)

        self.left_telemetry_panel = LeftTelemetryWidget()
        tl_layout.addWidget(self.left_telemetry_panel, alignment=Qt.AlignTop | Qt.AlignLeft)

        self.video_layout.addWidget(self.top_left_container, 0, 0, alignment=Qt.AlignTop | Qt.AlignLeft)

        # Top-right container for connection status and telemetry
        self.top_right_container = QWidget()
        tr_layout = QVBoxLayout(self.top_right_container)
        tr_layout.setContentsMargins(0, 10, 10, 10)
        tr_layout.setSpacing(20)

        self.conn_panel = ConnectionHud()
        tr_layout.addWidget(self.conn_panel, alignment=Qt.AlignTop | Qt.AlignRight)

        self.right_telemetry_panel = RightTelemetryWidget()
        tr_layout.addWidget(self.right_telemetry_panel, alignment=Qt.AlignTop | Qt.AlignRight)
        
        self.video_layout.addWidget(self.top_right_container, 0, 0, alignment=Qt.AlignTop | Qt.AlignRight)

        # Warning overlay
        self.warning_panel = WarningWidget()
        self.video_layout.addWidget(self.warning_panel, 0, 0)


    # --- INPUT EVENTS ---
    def keyPressEvent(self, event):
        if self.overlay.isVisible():
            super().keyPressEvent(event)
            return
        self.input.key_pressed(event)

    def keyReleaseEvent(self, event):
        self.input.key_released(event)
        super().keyReleaseEvent(event)

    # --- WINDOW MANAGEMENT ---
    def resizeEvent(self, event):
        self.overlay.resize_overlays(self.rect())
        super().resizeEvent(event)

    # --- HUD STATUS UPDATES ---
    def _update_video_status(self, connected):
        self.conn_panel.update_video_status(connected)

    def _update_control_status(self, connected):
        self.conn_panel.update_control_status(connected)

        if not connected:
            self.warning_panel.reset_ui()
            self.right_telemetry_panel.reset_ui()
            self.left_telemetry_panel.reset_ui()

    # --- VIDEO RENDERING ---
    def _update_frame(self):
        self._update_control_status(self.control.is_connected())

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
            self._update_video_status(False)
            return

        if time.time() - self.last_frame_time > UDP_TIMEOUT:
            self.video_label.setPixmap(QPixmap())
            self.waiting_label.show()
            self._update_video_status(False)
            return

        if not has_new or frame is None:
            return

        self.waiting_label.hide()
        self._update_video_status(True)

        win_w = self.video_label.width()
        win_h = self.video_label.height()

        pixmap = create_qpixmap(frame, win_w, win_h)
        self.video_label.setPixmap(pixmap)

    # --- FULLSCREEN MANAGEMENT ---
    def _create_actions(self):
        self.action__toggle_fullscreen = QAction("Toggle Fullscreen", self)
        self.action__toggle_fullscreen.setShortcut("F11")
        self.action__toggle_fullscreen.triggered.connect(self._toggle_fullscreen)
        self.addAction(self.action__toggle_fullscreen)

        self.action_toggle_menu = QAction("Toggle Menu", self)
        self.action_toggle_menu.setShortcut("Esc")
        self.action_toggle_menu.triggered.connect(self._toggle_menu_safely)
        self.addAction(self.action_toggle_menu)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showMaximized()
        else:
            self.showFullScreen()

    # --- OPEN MENUS SAFELY ---
    def _open_info_page_safely(self):
        self.input.current_command = "STOP"
        self.overlay.show_info_page()

    def _toggle_menu_safely(self):
        if not self.overlay.isVisible():
            self.input.current_command = "STOP"
        self.overlay.toggle_menu()

