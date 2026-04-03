from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from Video.styles import CONNECTION_PANEL_STYLE, TITLE_2_TEXT, TEXT_BOLD, ALERT_TEXT, WARNING_TEXT
from config import ALERT_CPU_TEMP, ALERT_HULL_HUM

class LeftTelemetryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(8)

        self.title = QLabel("RASPBERRY PI DATA")
        self.title.setStyleSheet(TITLE_2_TEXT)
        self.title.setContentsMargins(0, 0, 0, 15)
        layout.addWidget(self.title)

        self.tel_temp = QLabel("CPU TEMP: -- °C")
        self.tel_temp.setStyleSheet(TEXT_BOLD)
        layout.addWidget(self.tel_temp)
        
        self.tel_cpu = QLabel("CPU: -- %")
        self.tel_cpu.setStyleSheet(TEXT_BOLD)
        layout.addWidget(self.tel_cpu)

        self.tel_ram = QLabel("RAM: -- %")
        self.tel_ram.setStyleSheet(TEXT_BOLD)
        layout.addWidget(self.tel_ram)

        self.tel_power = QLabel("")
        self.tel_power.setStyleSheet(TEXT_BOLD)
        layout.addWidget(self.tel_power)

    def update_ui(self, data: dict):
        """ Triggered automatically by the network listener """
        self.tel_temp.setText(f"TEMP: {data['cpu_temp']} °C")
        self.tel_cpu.setText(f"CPU: {data['cpu_usage']} %")
        self.tel_ram.setText(f"RAM: {data['ram_usage']} %")
        
        if data['cpu_temp'] > ALERT_CPU_TEMP:
            self.tel_temp.setText(f"⚠️ CPU TEMP: {data['cpu_temp']} °C")
            self.tel_temp.setStyleSheet(ALERT_TEXT)
        else:
            self.tel_temp.setStyleSheet(TEXT_BOLD)

        if data.get('low_pwr', False):
            self.tel_power.setText("⚠️ WARNING! LOW VOLTAGE")
            self.tel_power.setStyleSheet(ALERT_TEXT)
        else:
            self.tel_power.setStyleSheet(TEXT_BOLD)

class RightTelemetryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(8)

        self.title = QLabel("DRONE DATA")
        self.title.setStyleSheet(TITLE_2_TEXT)
        self.title.setContentsMargins(0, 0, 0, 15)
        layout.addWidget(self.title)

        self.tel_front_pwr = QLabel("FRONT PWR: -- %")
        self.tel_front_pwr.setStyleSheet(TEXT_BOLD)
        layout.addWidget(self.tel_front_pwr)

        self.tel_rear_pwr = QLabel("REAR PWR: -- %")
        self.tel_rear_pwr.setStyleSheet(TEXT_BOLD)
        self.tel_rear_pwr.setContentsMargins(0, 0, 0, 15)
        layout.addWidget(self.tel_rear_pwr)


        self.tel_hull_temp = QLabel("HULL TEMP: -- °C")
        self.tel_hull_temp.setStyleSheet(TEXT_BOLD)
        layout.addWidget(self.tel_hull_temp)

        self.tel_hull_hum = QLabel("HULL HUM: -- %")
        self.tel_hull_hum.setStyleSheet(TEXT_BOLD)
        self.tel_hull_hum.setContentsMargins(0, 0, 0, 15)
        layout.addWidget(self.tel_hull_hum)

        self.tel_pitch = QLabel("PITCH: -- °")
        self.tel_pitch.setStyleSheet(TEXT_BOLD)
        layout.addWidget(self.tel_pitch)
        
        self.tel_roll = QLabel("ROLL: -- °")
        self.tel_roll.setStyleSheet(TEXT_BOLD)
        layout.addWidget(self.tel_roll)

    def update_ui(self, data: dict):
        front_pct = data.get("front_pwr", 0)
        rear_pct = data.get("front_pwr", 0)
        self.tel_front_pwr.setText(f"FRONT PWR: {front_pct} %")
        self.tel_rear_pwr.setText(f"REAR PWR: {rear_pct} %")

        hull_temp = data.get("hull_temp", 0.0)
        hull_hum = data.get("hull_hum", 0.0)
        self.tel_hull_temp.setText(f"HULL TEMP: {hull_temp} °C")
        self.tel_hull_hum.setText(f"HULL HUM: {hull_hum} %")

        if hull_hum > ALERT_HULL_HUM:
            self.tel_hull_hum.setText(f"⚠️ HULL HUM: {hull_hum} %")
            self.tel_hull_hum.setStyleSheet(ALERT_TEXT)
        else:
            self.tel_hull_hum.setStyleSheet(TEXT_BOLD)
        pass

        pitch = data.get("pitch", 0.0)
        roll = data.get("roll", 0.0)
        self.tel_pitch.setText(f"PITCH: {pitch} °")
        self.tel_roll.setText(f"ROLL: {roll} °")

class WarningWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 20)

        self.leak_label = QLabel("")
        self.leak_label.setStyleSheet(WARNING_TEXT)
        self.leak_label.hide()
        layout.addWidget(self.leak_label, alignment=Qt.AlignTop | Qt.AlignHCenter)

        layout.addStretch()

        self.camera_warning_label = QLabel("")
        self.camera_warning_label.setStyleSheet(WARNING_TEXT)
        self.camera_warning_label.hide()
        layout.addWidget(self.camera_warning_label, alignment=Qt.AlignCenter)

        layout.addStretch()

    def update_ui(self, data: dict):
        if data.get("leak_detected", False):
            self.leak_label.setText("WARNING! WATER DETECTED INSIDE THE HULL")
            self.leak_label.show()
        else:
            self.leak_label.hide()

        if not data.get("camera_status", True):
            self.camera_warning_label.setText("WARNING! CAMERA FAILED TO START. DRONE IS STILL DRIVABLE.")
            self.camera_warning_label.show()
        else:
            self.camera_warning_label.hide()

    def reset_ui(self):
        self.leak_label.hide()
        self.camera_warning_label.hide()
