import cv2
from PySide6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, 
    QWidget, QGridLayout, QStackedLayout, QGraphicsBlurEffect,
    QCheckBox
)
from PySide6.QtCore import Qt, QTimer, QSettings
from PySide6.QtGui import QImage, QPixmap, QAction
from config import WINDOW_NAME
from Video.settings_widget import SettingsWidget
from Video.help_widget import HelpWidget

class VideoWindow(QMainWindow):
    def __init__(self, frame_buffer, control_client):
        super().__init__()
        self.fb = frame_buffer
        self.control = control_client
        self.current_command = "STOP\n"
        self.is_true_fullscreen = False

        self.setWindowTitle(WINDOW_NAME)

        # 1. Setup Data & Timers
        self._setup_bindings()

        self.control_timer = QTimer()
        self.control_timer.timeout.connect(self.send_control)
        self.control_timer.start(100)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(32)

        # 2. Setup the User Interface
        self._setup_ui()
        self._create_actions()

        # 3. Final Window Config
        self.showMaximized()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        if self.settings.value("show_help_on_startup", True, type=bool):
            self.show_help_overlay()

    def _setup_bindings(self):
        """ Initializes QSettings and loads saved keybinds. """
        self.settings = QSettings("UnderwaterDrone", "DroneClient")
        self.default_bindings = {
            "W\n": Qt.Key_W, "S\n": Qt.Key_S, "A\n": Qt.Key_A, "D\n": Qt.Key_D,
            "UP\n": Qt.Key_U, "DOWN\n": Qt.Key_J,
            "REAR+\n": Qt.Key_O, "REAR-\n": Qt.Key_L,
            "FRONT+\n": Qt.Key_I, "FRONT-\n": Qt.Key_K
        }
        self.bindings = {}
        self.key_to_cmd = {}
        self.load_bindings()

    def _setup_ui(self):
        """ Builds the main video layouts and overlay stack. """
        central = QWidget()
        self.setCentralWidget(central)

        self.stack = QStackedLayout(central)
        self.stack.setContentsMargins(0, 0, 0, 0)

        # Video container
        self.video_container = QWidget()
        self.video_layout = QGridLayout(self.video_container)
        self.video_layout.setContentsMargins(0, 0, 0, 0)

        self.video_label = QLabel(alignment=Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: #0D0D0D;")
        self.video_layout.addWidget(self.video_label, 0, 0)

        # Waiting label
        self.waiting_label = QLabel("WAITING FOR STREAM...", alignment=Qt.AlignCenter)
        self.waiting_label.setStyleSheet("""
            font-family: 'Segoe Ui'; color: white; font-size: 40px; 
            font-weight: bold; background: transparent;
        """)
        self.video_layout.addWidget(self.waiting_label, 0, 0, alignment=Qt.AlignCenter)

        self.stack.addWidget(self.video_container)

        # Menu overlay setup
        self.menu_overlay = self._create_overlay()
        self.menu_overlay.setParent(self.centralWidget()) 
        self.menu_overlay.setGeometry(self.rect()) 
        self.menu_overlay.hide()

        # Floating Help Button
        self.info_button = QPushButton("INFO")
        self.info_button.setFixedSize(90, 50)
        self.info_button.setStyleSheet("""
            QPushButton {
                font-family: 'Segoe Ui'; background-color: #333; color: white;
                border: 1px solid #444; border-radius: 5px;
                font-size: 16px; font-weight: bold; margin: 10px;
            }
            QPushButton:hover { background-color: #444444; border: 1px solid #666; }
        """)
        self.video_layout.addWidget(self.info_button, 0, 0, alignment=Qt.AlignTop | Qt.AlignLeft)
        self.info_button.clicked.connect(self.show_help_overlay)

    def _create_overlay(self):
        """ Builds the paused menu and links the settings widget. """
        overlay = QWidget(self.centralWidget())
        overlay.setObjectName("BaseOverlay")
        overlay.setStyleSheet("#BaseOverlay { background-color: rgba(40, 40, 40, 180); }")
        self.overlay_stack = QStackedLayout(overlay)

        # PAGE 0: MAIN MENU
        main_menu_widget = QWidget()
        main_outer_layout = QVBoxLayout(main_menu_widget)
        main_outer_layout.setAlignment(Qt.AlignCenter)

        menu_panel = QWidget()
        menu_panel.setObjectName("MenuPanel")
        menu_panel.setStyleSheet("""
            #MenuPanel { background-color: #1A1A1A; border-radius: 15px; border: 2px solid #333; }
        """)
        menu_panel.setFixedWidth(350)
        
        menu_layout = QVBoxLayout(menu_panel)
        menu_layout.setAlignment(Qt.AlignCenter)
        menu_layout.setSpacing(20)
        menu_layout.setContentsMargins(40, 40, 40, 40) 

        title = QLabel("MAIN MENU")
        title.setStyleSheet("""
            font-family: 'Segoe Ui'; font-size: 30px; font-weight: bold;
            color: white; margin-bottom: 18px; background: transparent;
        """)
        title.setAlignment(Qt.AlignCenter)
        menu_layout.addWidget(title)

        button_style = """
            QPushButton {
                background-color: #333; color: white;
                border: 2px solid #444; border-radius: 5px;
                font-family: 'Segoe Ui'; font-size: 20px; 
                font-weight: bold;
            }
            QPushButton:hover { background-color: #444444; border: 2px solid #666; }
        """

        resume_btn = QPushButton("RESUME")
        settings_btn = QPushButton("SETTINGS")
        quit_btn = QPushButton("QUIT")

        for btn in (resume_btn, settings_btn, quit_btn):
            btn.setFixedHeight(50)
            btn.setFixedWidth(200)
            btn.setStyleSheet(button_style)
            menu_layout.addWidget(btn)

        main_outer_layout.addWidget(menu_panel)

        resume_btn.clicked.connect(self.toggle_overlay)
        settings_btn.clicked.connect(self.show_settings_page)
        quit_btn.clicked.connect(self.close)

        # PAGE 1: SETTINGS MENU
        self.settings_page = SettingsWidget(self.bindings, self)
        self.settings_page.save_btn.clicked.connect(self.save_and_return)

        # PAGE 2: HELP MENU
        self.info_page = HelpWidget(self)
        self.info_page.close_btn.clicked.connect(self.close_help_overlay)

        self.overlay_stack.addWidget(main_menu_widget)
        self.overlay_stack.addWidget(self.settings_page)
        self.overlay_stack.addWidget(self.info_page)

        return overlay

    # --- SETTINGS MANAGEMENT ---
    def load_bindings(self):
        """ Loads keys from the hard drive """
        for cmd, default_key in self.default_bindings.items():
            # Grabs the saved key, or uses the default if it doesn't exist yet
            self.bindings[cmd] = self.settings.value(cmd, default_key, type=int)
            
        # Create a reverse dictionary (Key -> Command) for lightning fast lookups
        self.key_to_cmd = {v: k for k, v in self.bindings.items()}

    def save_bindings(self, new_bindings):
        """ Saves keys to the hard drive """
        for cmd, key in new_bindings.items():
            self.settings.setValue(cmd, key)
        self.load_bindings()

    def show_settings_page(self):
        """ Slide to the Settings Page """
        self.overlay_stack.setCurrentIndex(1)

    def save_and_return(self):
        """ Save keys and return to the Main Menu """
        new_bindings = self.settings_page.get_new_bindings()
        self.save_bindings(new_bindings)
        self.overlay_stack.setCurrentIndex(0)
        print("[DEBUG] Keybindings saved successfully!")

    # --- CONTROL & EVENTS ---
    def send_control(self):
        """ Sends the continuous heartbeat to the drone """
        if self.control and self.control.sock:
            self.control.send(self.current_command)

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return

        key = event.key()

        if key == Qt.Key_Escape:
            self.toggle_overlay()
            return

        cmd = self.key_to_cmd.get(key)
        if not cmd:
            return

        movement_cmds = {"W\n", "S\n", "A\n", "D\n", "UP\n", "DOWN\n"}
        if cmd in movement_cmds:
            self.current_command = cmd
        else:
            self.control.send(cmd)

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat(): 
            return

        key = event.key()
        cmd = self.key_to_cmd.get(key)
            
        movement_cmds = {"W\n", "S\n", "A\n", "D\n", "UP\n", "DOWN\n"}
        if cmd in movement_cmds:
            self.current_command = "STOP\n"

    def toggle_overlay(self):
        if self.menu_overlay.isVisible():
            current_idx = self.overlay_stack.currentIndex()

            if current_idx == 1:
                self.overlay_stack.setCurrentIndex(0)
            elif current_idx == 2:
                self.close_help_overlay()
            else:
                self.video_label.setGraphicsEffect(None)
                self.menu_overlay.hide()
                self.overlay_stack.setCurrentIndex(0)
        else:
            blur = QGraphicsBlurEffect()
            blur.setBlurRadius(60)
            self.video_container.setGraphicsEffect(blur)

            self.menu_overlay.setGeometry(self.centralWidget().rect())
            self.menu_overlay.show()
            self.menu_overlay.raise_()

    def resizeEvent(self, event):
        self.menu_overlay.setGeometry(self.rect())
        super().resizeEvent(event)

    # --- VIDEO RENDERING ---
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

    # --- FULLSCREEN MANAGEMENT ---
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

    # --- HELP OVERLAY MANAGEMENT ---
    def show_help_overlay(self):
        """ Opens the help menu and applies the background blur """
        show_help = self.settings.value("show_help_on_startup", True, type=bool)
        self.info_page.dont_show_cb.setChecked(not show_help)

        if not self.menu_overlay.isVisible():
            blur = QGraphicsBlurEffect()
            blur.setBlurRadius(100)
            self.video_container.setGraphicsEffect(blur)
            
            self.menu_overlay.setGeometry(self.centralWidget().rect())
            self.menu_overlay.show()
            self.menu_overlay.raise_()
            
        self.overlay_stack.setCurrentIndex(2)

    def close_help_overlay(self):
        """ Saves the checkbox preference and closes the menu """
        dont_show = self.info_page.dont_show_cb.isChecked()
        self.settings.setValue("show_help_on_startup", not dont_show)
        
        self.video_container.setGraphicsEffect(None)
        self.menu_overlay.hide()
        self.overlay_stack.setCurrentIndex(0)
