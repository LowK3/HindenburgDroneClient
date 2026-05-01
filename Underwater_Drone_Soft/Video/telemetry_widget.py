from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from Video.artificial_horizon_widget import ArtificialHorizon
from Video.styles import (
    CONNECTION_PANEL_STYLE, TITLE_2_TEXT, TEXT_BOLD, ALERT_TEXT, WARNING_TEXT,
    CRITICAL_WARNING_TEXT
)
from config import ALERT_CPU_TEMP, ALERT_HULL_HUM, ALERT_HULL_TEMP

class LeftTelemetryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self.title = QLabel("RASPBERRY PI DATA")
        self.title.setStyleSheet(TITLE_2_TEXT)
        layout.addWidget(self.title)

        self.tel_temp = QLabel("CPU TEMP: -- °C")
        self.tel_temp.setStyleSheet(TEXT_BOLD)
        layout.addSpacing(15)
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
        self._update_alert_label(self.tel_temp, data.get("cpu_temp"), "CPU TEMP", "°C", ALERT_CPU_TEMP)

        cpu_usg = data.get("cpu_usg")
        ram_usg = data.get("ram_usg")
        cpu_str = cpu_usg if cpu_usg is not None else "--"
        ram_str = ram_usg if ram_usg is not None else "--"
        self.tel_cpu.setText(f"CPU: {cpu_str} %")
        self.tel_ram.setText(f"RAM: {ram_str} %")

        low_pwr = data.get("low_pwr", False)
        if low_pwr:
            self.tel_power.setText("⚠️ WARNING! LOW VOLTAGE")
            self.tel_power.setStyleSheet(ALERT_TEXT)
        else:
            self.tel_power.setText("")
            self.tel_power.setStyleSheet(TEXT_BOLD)

    def reset_ui(self):
        self.tel_temp.setText("CPU TEMP: -- °C")
        self.tel_cpu.setText("CPU: -- %")
        self.tel_ram.setText("RAM: -- %")
        self.tel_power.setText("")

    def _update_alert_label(self, label, value, prefix, unit, threshold):
        if value is not None:
            if value > threshold:
                label.setText(f"⚠️ {prefix}: {value} {unit}")
                label.setStyleSheet(ALERT_TEXT)
            else:
                label.setText(f"{prefix}: {value} {unit}")
                label.setStyleSheet(TEXT_BOLD)
        else:
            label.setText(f"{prefix}: -- {unit}")
            label.setStyleSheet(TEXT_BOLD)

class RightTelemetryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self.horizon = ArtificialHorizon()
        layout.addWidget(self.horizon, alignment=Qt.AlignHCenter)

        self.title = QLabel("DRONE DATA")
        self.title.setStyleSheet(TITLE_2_TEXT)
        self.title.setAlignment(Qt.AlignRight)
        layout.addSpacing(25)
        layout.addWidget(self.title)

        self.tel_front_pwr = QLabel("FRONT PWR: -- %")
        self.tel_front_pwr.setStyleSheet(TEXT_BOLD)
        self.tel_front_pwr.setAlignment(Qt.AlignRight)
        layout.addSpacing(15)
        layout.addWidget(self.tel_front_pwr)

        self.tel_rear_pwr = QLabel("REAR PWR: -- %")
        self.tel_rear_pwr.setStyleSheet(TEXT_BOLD)
        self.tel_rear_pwr.setAlignment(Qt.AlignRight)
        layout.addWidget(self.tel_rear_pwr)


        self.tel_hull_temp = QLabel("HULL TEMP: -- °C")
        self.tel_hull_temp.setStyleSheet(TEXT_BOLD)
        self.tel_hull_temp.setAlignment(Qt.AlignRight)
        layout.addSpacing(15)
        layout.addWidget(self.tel_hull_temp)

        self.tel_hull_hum = QLabel("HULL HUM: -- %")
        self.tel_hull_hum.setStyleSheet(TEXT_BOLD)
        self.tel_hull_hum.setAlignment(Qt.AlignRight)
        layout.addWidget(self.tel_hull_hum)

        self.tel_hull_press = QLabel("HULL PRESS: -- mbar")
        self.tel_hull_press.setStyleSheet(TEXT_BOLD)
        self.tel_hull_press.setAlignment(Qt.AlignRight)
        layout.addWidget(self.tel_hull_press)

    def update_ui(self, data: dict): 
        front_pwr = data.get("front_pwr")
        rear_pwr = data.get("rear_pwr") 
        front_pwr_str = front_pwr if front_pwr is not None else "--"
        rear_pwr_str = rear_pwr if rear_pwr is not None else "--"
        self.tel_front_pwr.setText(f"FRONT PWR: {front_pwr_str} %")
        self.tel_rear_pwr.setText(f"REAR PWR: {rear_pwr_str} %")

        self._update_alert_label(self.tel_hull_temp, data.get("hull_temp"), "HULL TEMP", "°C", ALERT_HULL_TEMP)
        self._update_alert_label(self.tel_hull_hum, data.get("hull_hum"), "HULL HUM", "%", ALERT_HULL_HUM)

        hull_press = data.get("hull_press")
        hull_press_str = hull_press if hull_press is not None else "--"
        self.tel_hull_press.setText(f"HULL PRESS: {hull_press_str} mbar")

        pitch = data.get("pitch", 0.0)
        roll = data.get("roll", 0.0)
        self.horizon.update_angles(pitch, roll)

    def reset_ui(self):
        self.tel_hull_temp.setText("HULL TEMP: -- °C")
        self.tel_hull_hum.setText("HULL HUM: -- %")
        self.tel_hull_press.setText("HULL PRESS: -- mbar")
        self.tel_front_pwr.setText("FRONT PWR: -- %")
        self.tel_rear_pwr.setText("REAR PWR: -- %")

    def _update_alert_label(self, label, value, prefix, unit, threshold):
        if value is not None:
            if value > threshold:
                label.setText(f"⚠️ {prefix}: {value} {unit}")
                label.setStyleSheet(ALERT_TEXT)
            else:
                label.setText(f"{prefix}: {value} {unit}")
                label.setStyleSheet(TEXT_BOLD)
        else:
            label.setText(f"{prefix}: -- {unit}")
            label.setStyleSheet(TEXT_BOLD)

class WarningWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 30, 10, 30)

        self.leak_label = QLabel("")
        self.leak_label.setStyleSheet(CRITICAL_WARNING_TEXT)
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
            self.leak_label.setText("WARNING! WATER DETECTED INSIDE THE HULL.")
            self.leak_label.show()
        else:
            self.leak_label.hide()

        if not data.get("camera_status", True):
            self.camera_warning_label.setText("ERROR! CAMERA FAILED. DRONE IS STILL DRIVABLE.")
            self.camera_warning_label.show()
        else:
            self.camera_warning_label.hide()

    def reset_ui(self):
        self.leak_label.hide()
        self.camera_warning_label.hide()
