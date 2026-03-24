from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from Video.styles import CONNECTION_PANEL_STYLE, TITLE_2_TEXT, TEXT_BOLD, ALERT_TEXT, WARNING_TEXT

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

        self.tel_temp = QLabel("CPU TEMP: -- °C")
        self.tel_temp.setStyleSheet(TEXT_BOLD)
        
        self.tel_cpu = QLabel("CPU: -- %")
        self.tel_cpu.setStyleSheet(TEXT_BOLD)

        self.tel_ram = QLabel("RAM: -- %")
        self.tel_ram.setStyleSheet(TEXT_BOLD)

        self.tel_power = QLabel("")
        self.tel_power.setStyleSheet(TEXT_BOLD)

        layout.addWidget(self.title)
        layout.addWidget(self.tel_temp)
        layout.addWidget(self.tel_cpu)
        layout.addWidget(self.tel_ram)
        layout.addWidget(self.tel_power)

    def update_ui(self, data):
        """ Triggered automatically by the network listener """
        self.tel_temp.setText(f"TEMP: {data['cpu_temp']} °C")
        self.tel_cpu.setText(f"CPU: {data['cpu_usage']} %")
        self.tel_ram.setText(f"RAM: {data['ram_usage']} %")
        
        if data['cpu_temp'] > 75.0:
            self.tel_temp.setText(f"⚠️ CPU TEMP: {data['cpu_temp']} °C")
            self.tel_temp.setStyleSheet(ALERT_TEXT)
        else:
            self.tel_temp.setStyleSheet(TEXT_BOLD)

        if data.get('low_power', False):
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

        self.tel_front_pwr = QLabel("FRONT PWR: -- %")
        self.tel_front_pwr.setStyleSheet(TEXT_BOLD)

        self.tel_rear_pwr = QLabel("REAR PWR: -- %")
        self.tel_rear_pwr.setStyleSheet(TEXT_BOLD)

        layout.addWidget(self.title)
        layout.addWidget(self.tel_front_pwr)
        layout.addWidget(self.tel_rear_pwr)

    def update_ui(self, data):
        rear_pct = data.get('rear_power', 0)
        front_pct = data.get('front_power', 0)
        
        self.tel_rear_pwr.setText(f"FWD PWR: {rear_pct} %")
        self.tel_front_pwr.setText(f"TILT PWR: {front_pct} %")
        pass

class WarningWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 0)

        self.leak_label = QLabel("")
        self.leak_label.setStyleSheet(WARNING_TEXT)
        self.leak_label.hide()

        layout.addWidget(self.leak_label, alignment=Qt.AlignTop | Qt.AlignHCenter)

    def update_ui(self, data):
        if data.get('leak_detected', False):
            self.leak_label.setText("WARNING! WATER DETECTED INSIDE THE HULL")
            self.leak_label.show()
        else:
            self.leak_label.hide()