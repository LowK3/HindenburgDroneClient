import pygame
from PySide6.QtCore import QObject, QTimer, Qt, QSettings, Signal
from config import (
    GUI_REFRESH_RATE, HEARTBEAT_INTERVAL, JOYSTICK_DEADZONE, 
    POWER_STEP, POWER_MIN, POWER_MAX, AXIS_YAW, AXIS_FWD, 
    AXIS_DEPTH, AXIS_DEPTH_ALT, DEFAULT_POWER_SCALE
)

class InputManager(QObject):
    """ Maps hardware and keyboard inputs to a continuous proportional axis payload. """
    command_requested = Signal(dict)
    front_power_changed = Signal(int)
    rear_power_changed = Signal(int)

    def __init__(self):
        super().__init__()
        
        self.settings = QSettings("UnderwaterDrone", "DroneClient")
        self.default_bindings = {
            "FORWARD": Qt.Key_W, "BACKWARD": Qt.Key_S,
            "TURN_LEFT": Qt.Key_A, "TURN_RIGHT": Qt.Key_D,
            "TILT_UP": Qt.Key_E, "TILT_DOWN": Qt.Key_Q,
            "REAR_PWR_INC": Qt.Key_O, "REAR_PWR_DEC": Qt.Key_L,
            "FRONT_PWR_INC": Qt.Key_I, "FRONT_PWR_DEC": Qt.Key_K
        }
        self.bindings = {}
        self.key_to_cmd = {}
        self.load_bindings()

        self.held_keys = set()
        
        self.front_power = DEFAULT_POWER_SCALE
        self.rear_power = DEFAULT_POWER_SCALE

        pygame.display.init()
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        self.ticks_since_last_send = 0

        self.control_timer = QTimer(self)
        self.control_timer.timeout.connect(self._poll_inputs)
        self.control_timer.start(GUI_REFRESH_RATE)

    def load_bindings(self):
        for cmd, default_key in self.default_bindings.items():
            self.bindings[cmd] = self.settings.value(cmd, default_key, type=int)
        self.key_to_cmd = {v: k for k, v in self.bindings.items()}

    def save_bindings(self, new_bindings: dict):
        for cmd, key in new_bindings.items():
            self.settings.setValue(cmd, key)
        self.load_bindings()

    def _apply_deadzone(self, value: float) -> float:
        return 0.0 if abs(value) < JOYSTICK_DEADZONE else value

    def _poll_inputs(self):
        pygame.event.pump()
        
        joy_fwd, joy_yaw, joy_depth = 0.0, 0.0, 0.0
        
        if self.joystick:
            joy_fwd = -self._apply_deadzone(self.joystick.get_axis(AXIS_FWD))
            joy_yaw = self._apply_deadzone(self.joystick.get_axis(AXIS_YAW))
            
            depth_idx = AXIS_DEPTH if self.joystick.get_numaxes() > AXIS_DEPTH else AXIS_DEPTH_ALT
            if self.joystick.get_numaxes() > depth_idx:
                joy_depth = -self._apply_deadzone(self.joystick.get_axis(depth_idx))

        kb_fwd = 1.0 if "FORWARD" in self.held_keys else (-1.0 if "BACKWARD" in self.held_keys else 0.0)
        kb_yaw = 1.0 if "TURN_RIGHT" in self.held_keys else (-1.0 if "TURN_LEFT" in self.held_keys else 0.0)
        kb_depth = 1.0 if "TILT_UP" in self.held_keys else (-1.0 if "TILT_DOWN" in self.held_keys else 0.0)

        final_fwd = joy_fwd if joy_fwd != 0.0 else kb_fwd
        final_yaw = joy_yaw if joy_yaw != 0.0 else kb_yaw
        final_depth = joy_depth if joy_depth != 0.0 else kb_depth

        scaled_fwd = final_fwd * self.rear_power
        scaled_yaw = final_yaw * self.rear_power
        scaled_depth = final_depth * self.front_power

        is_moving = any([scaled_fwd, scaled_yaw, scaled_depth])
        self.ticks_since_last_send += GUI_REFRESH_RATE
        
        if is_moving or self.ticks_since_last_send >= HEARTBEAT_INTERVAL:
            if is_moving:
                payload = {
                    "cmd": "AXIS",
                    "axes": {
                        "fwd": round(scaled_fwd, 3),
                        "yaw": round(scaled_yaw, 3),
                        "depth": round(scaled_depth, 3)
                    }
                }
            else:
                payload = {"cmd": "PING"}
                
            self.command_requested.emit(payload)
            self.ticks_since_last_send = 0

    def key_pressed(self, event):
        if event.isAutoRepeat(): 
            return
        cmd = self.key_to_cmd.get(event.key())
        if not cmd: 
            return

        if cmd in {"FORWARD", "BACKWARD", "TURN_LEFT", "TURN_RIGHT", "TILT_UP", "TILT_DOWN"}:
            self.held_keys.add(cmd)
        elif cmd == "REAR_PWR_INC":
            self.rear_power = min(POWER_MAX, self.rear_power + POWER_STEP)
            self.rear_power_changed.emit(round(self.rear_power * 100))
        elif cmd == "REAR_PWR_DEC":
            self.rear_power = max(POWER_MIN, self.rear_power - POWER_STEP)
            self.rear_power_changed.emit(round(self.rear_power * 100))
        elif cmd == "FRONT_PWR_INC":
            self.front_power = min(POWER_MAX, self.front_power + POWER_STEP)
            self.front_power_changed.emit(round(self.front_power * 100))
        elif cmd == "FRONT_PWR_DEC":
            self.front_power = max(POWER_MIN, self.front_power - POWER_STEP)
            self.front_power_changed.emit(round(self.front_power * 100))

    def key_released(self, event):
        if event.isAutoRepeat(): 
            return
        cmd = self.key_to_cmd.get(event.key())
        if cmd in self.held_keys:
            self.held_keys.remove(cmd)