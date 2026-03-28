from PySide6.QtCore import QObject, QTimer, Qt, QSettings
from Utils.logger import log
from config import HEARTBEAT_SEND

class InputManager(QObject):
    """ Handles keybinds, saving settings, and sending network commands. """
    def __init__(self, control_client, status_callback):
        super().__init__()
        self.control = control_client
        self.update_status_ui = status_callback # Callback to change the HUD dot green/red
        self.current_command = "STOP"
        
        # Initializes QSettings and loads saved keybinds.
        self.settings = QSettings("UnderwaterDrone", "DroneClient")
        self.default_bindings = {
            "W": Qt.Key_W, "S": Qt.Key_S, "A": Qt.Key_A, "D": Qt.Key_D,
            "UP": Qt.Key_U, "DOWN": Qt.Key_J,
            "REAR+": Qt.Key_O, "REAR-": Qt.Key_L,
            "FRONT+": Qt.Key_I, "FRONT-": Qt.Key_K
        }
        self.bindings = {}
        self.key_to_cmd = {}
        self.load_bindings()

        # Start the network heartbeat loop
        self.control_timer = QTimer(self)
        self.control_timer.timeout.connect(self.send_control)
        self.control_timer.start(HEARTBEAT_SEND)

    def load_bindings(self):
        for cmd, default_key in self.default_bindings.items():
            # Grabs the saved key, or uses the default if it doesn't exist yet
            self.bindings[cmd] = self.settings.value(cmd, default_key, type=int)
        # Create a reverse dictionary (Key -> Command) for fast lookups
        self.key_to_cmd = {v: k for k, v in self.bindings.items()}

    def save_bindings(self, new_bindings):
        for cmd, key in new_bindings.items():
            self.settings.setValue(cmd, key)
        self.load_bindings()

    def send_control(self):
        """ Sends the continuous heartbeat to the drone """
        if self.control and self.control.sock:
            self.update_status_ui(True)
            try:
                self.control.send({"cmd": self.current_command})
            except Exception:
                self.update_status_ui(False)
        else:
            self.update_status_ui(False)

    def key_pressed(self, event):
        if event.isAutoRepeat(): 
            return
        cmd = self.key_to_cmd.get(event.key())
        if not cmd: 
            return

        if cmd in {"W", "S", "A", "D", "UP", "DOWN"}:
            self.current_command = cmd
        else:
            self.control.send({"cmd": cmd})

    def key_released(self, event):
        if event.isAutoRepeat(): 
            return
        cmd = self.key_to_cmd.get(event.key())
        if cmd in {"W", "S", "A", "D", "UP", "DOWN"}:
            self.current_command = "STOP"