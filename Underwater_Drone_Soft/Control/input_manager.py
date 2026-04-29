from PySide6.QtCore import QObject, QTimer, Qt, QSettings, Signal
from config import HEARTBEAT_INTERVAL

class InputManager(QObject):
    """ Handles keybinds, saving settings, and sending network commands. """
    command_requested = Signal(dict)

    def __init__(self):
        super().__init__()
        self.current_command = "STOP"
        
        # Initializes QSettings and loads saved keybinds.
        self.settings = QSettings("HindenburgDrone", "DroneClient")
        self.default_bindings = {
            "W": Qt.Key_W, "S": Qt.Key_S, "A": Qt.Key_A, "D": Qt.Key_D,
            "UP": Qt.Key_E, "DOWN": Qt.Key_Q,
            "REAR+": Qt.Key_O, "REAR-": Qt.Key_L,
            "FRONT+": Qt.Key_I, "FRONT-": Qt.Key_K
        }
        self.bindings = {}
        self.key_to_cmd = {}
        self.load_bindings()

        # Start the network heartbeat loop
        self.control_timer = QTimer(self)
        self.control_timer.timeout.connect(self._send_heartbeat)
        self.control_timer.start(HEARTBEAT_INTERVAL)

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

    def _send_heartbeat(self):
        self.command_requested.emit({"cmd": "PING"})

    def key_pressed(self, event):
        if event.isAutoRepeat(): 
            return
        cmd = self.key_to_cmd.get(event.key())
        if not cmd: 
            return

        self.current_command = cmd
        self.command_requested.emit({"cmd": cmd})

    def key_released(self, event):
        if event.isAutoRepeat(): 
            return
        cmd = self.key_to_cmd.get(event.key())
        if cmd in {"W", "S", "A", "D", "UP", "DOWN"}:
            if self.current_command == cmd:
                self.current_command = "STOP"
                self.command_requested.emit({"cmd": "STOP"})