import cv2, time
from PySide6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, 
    QWidget, QGridLayout, QStackedLayout, QGraphicsBlurEffect,
    QCheckBox, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer, QSettings
from PySide6.QtGui import QImage, QPixmap, QAction
from config import WINDOW_NAME
from Video.settings_widget import SettingsWidget
from Video.info_widget import InfoWidget
from Video.tutorial_widget import TutorialWidget

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
        self.last_frame_time = time.time()

        # 2. Setup the User Interface
        self._setup_ui()
        self._create_actions()

        # 3. Final Window Config
        self.showMaximized()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        if self.settings.value("show_info_on_startup", True, type=bool):
            self.show_info_page()

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

        # Floating Info Button
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
        self.info_button.clicked.connect(self.show_info_page)

        # Connection Status Hud
        self.conn_panel = QWidget()
        self.conn_panel.setStyleSheet("""
            QWidget {
                background-color: #333; border: 1px solid #444;
                border-radius: 5px; margin: 10px;
            }
            QLabel {
                font-family: 'Segoe Ui'; background: transparent; color: white; font-size: 14px;
                font-weight: bold; border: none; margin-left: 0px; margin-right: 0px;
            }
            QLabel#StatusDot {
                min-width: 14px; min-height: 14px; 
                max-width: 14px; max-height: 14px;
                border-radius: 6px; 
            }
        """)
        
        conn_layout = QHBoxLayout(self.conn_panel)
        conn_layout.setContentsMargins(20, 7, 20, 7)
        conn_layout.setSpacing(5)

        self.vid_dot = QLabel()
        self.vid_dot.setFixedSize(12, 12)
        self.vid_dot.setObjectName("StatusDot")
        self.vid_dot.setStyleSheet("background-color: #FF3333;") 
        self.vid_text = QLabel("VIDEO")

        conn_layout.addWidget(self.vid_dot)
        conn_layout.addWidget(self.vid_text)
        conn_layout.addSpacing(25)

        self.ctrl_dot = QLabel()
        self.ctrl_dot.setObjectName("StatusDot")
        self.ctrl_dot.setStyleSheet("background-color: #FF3333;") 
        self.ctrl_text = QLabel("CONTROL")

        conn_layout.addWidget(self.ctrl_dot)
        conn_layout.addWidget(self.ctrl_text)

        self.video_layout.addWidget(self.conn_panel, 0, 0, alignment=Qt.AlignTop | Qt.AlignRight)

    def _create_overlay(self):
        """ Builds the paused menu and links the settings widget. """
        overlay = QWidget(self.centralWidget())
        overlay.setObjectName("BaseOverlay")
        overlay.setStyleSheet("#BaseOverlay { background-color: rgba(40, 40, 40, 180); }")
        self.overlay_stack = QStackedLayout(overlay)

        # Page 0: MAIN MENU
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

        # Page 1: SETTINGS MENU
        self.settings_page = SettingsWidget(self.bindings, self)
        self.settings_page.save_btn.clicked.connect(self.save_and_return)

        # Page 2: INDO MENU
        self.info_page = InfoWidget(self)
        self.info_page.close_btn.clicked.connect(self.close_info_page)

        # Page 3: TUTORIAL MENU
        self.tutorial_page = TutorialWidget(self)
        self.info_page.tutorial_btn.clicked.connect(self.show_tutorial_page)
        self.tutorial_page.back_btn.clicked.connect(self.close_tutorial_page)

        self.overlay_stack.addWidget(main_menu_widget)
        self.overlay_stack.addWidget(self.settings_page)
        self.overlay_stack.addWidget(self.info_page)
        self.overlay_stack.addWidget(self.tutorial_page)

        return overlay

    # --- SETTINGS MANAGEMENT ---
    def load_bindings(self):
        """ Loads keys from the hard drive """
        for cmd, default_key in self.default_bindings.items():
            # Grabs the saved key, or uses the default if it doesn't exist yet
            self.bindings[cmd] = self.settings.value(cmd, default_key, type=int)
            
        # Create a reverse dictionary (Key -> Command) for fast lookups
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
            self.update_control_status(True)
            try:
                self.control.send(self.current_command)
            except Exception:
                self.update_control_status(False)
        else:
            self.update_control_status(False)

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return

        key = event.key()

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

    # --- OVERLAY AND WINDOW MANAGEMENT ---
    def toggle_overlay(self):
        if self.menu_overlay.isVisible():
            current_idx = self.overlay_stack.currentIndex()

            if current_idx == 1:
                self.overlay_stack.setCurrentIndex(0)
            elif current_idx == 2:
                self.close_info_page()
            elif current_idx == 3:
                self.close_tutorial_page()
            else:
                self.video_label.setGraphicsEffect(None)
                self.menu_overlay.hide()
                self.overlay_stack.setCurrentIndex(0)
                self.setFocus()
        else:
            blur = QGraphicsBlurEffect()
            blur.setBlurRadius(100)
            self.video_container.setGraphicsEffect(blur)

            self.menu_overlay.setGeometry(self.centralWidget().rect())
            self.menu_overlay.show()
            self.menu_overlay.raise_()
            self.setFocus()

    def resizeEvent(self, event):
        self.menu_overlay.setGeometry(self.rect())
        super().resizeEvent(event)

    def show_info_page(self):
        """ Opens the info menu and applies the background blur """
        show_info = self.settings.value("show_info_on_startup", True, type=bool)
        self.info_page.dont_show_cb.setChecked(not show_info)

        if not self.menu_overlay.isVisible():
            blur = QGraphicsBlurEffect()
            blur.setBlurRadius(100)
            self.video_container.setGraphicsEffect(blur)
            
            self.menu_overlay.setGeometry(self.centralWidget().rect())
            self.menu_overlay.show()
            self.menu_overlay.raise_()
            
        self.overlay_stack.setCurrentIndex(2)

    def close_info_page(self):
        """ Saves the checkbox preference and closes the menu """
        dont_show = self.info_page.dont_show_cb.isChecked()
        self.settings.setValue("show_info_on_startup", not dont_show)
        
        self.video_container.setGraphicsEffect(None)
        self.menu_overlay.hide()
        self.overlay_stack.setCurrentIndex(0)

    def show_tutorial_page(self):
        self.overlay_stack.setCurrentIndex(3)
        self.setFocus()

    def close_tutorial_page(self):
        self.overlay_stack.setCurrentIndex(2)
        self.setFocus()

    # --- HUD STATUS UPDATES ---
    def update_video_status(self, connected):
        if connected:
            self.vid_dot.setStyleSheet("background-color: #33FF33;")
        else:
            self.vid_dot.setStyleSheet("background-color: #FF3333;")

    def update_control_status(self, connected):
        if connected:
            self.ctrl_dot.setStyleSheet("background-color: #33FF33;")
        else:
            self.ctrl_dot.setStyleSheet("background-color: #FF3333;")

    # --- VIDEO RENDERING ---
    def update_frame(self):
        if self.menu_overlay.isVisible():
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

        # 3. THE WATCHDOG: Has it been more than 1 seconds since the last frame?
        if time.time() - self.last_frame_time > 1:
            self.video_label.setPixmap(QPixmap()) # Clear the frozen picture
            self.waiting_label.show()             # Show the "WAITING" text
            self.update_video_status(False)       # Turn the dot RED
            return

        # 4. If we don't have a new frame right this instant (but haven't timed out yet), just wait.
        if not has_new or frame is None:
            return

        self.waiting_label.hide()
        self.update_video_status(True)

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

        self.action_toggle_menu = QAction("Toggle Menu", self)
        self.action_toggle_menu.setShortcut("Esc")
        self.action_toggle_menu.triggered.connect(self.toggle_overlay)
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

