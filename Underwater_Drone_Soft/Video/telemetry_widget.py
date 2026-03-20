from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from Video.styles import CONNECTION_PANEL_STYLE, TITLE_2_TEXT, TEXT_BOLD, ALERT_TEXT

class TelemetryWidget(QWidget):
    telemetry_received = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(8)

        self.title = QLabel("RASPBERRY PI DATA")
        self.title.setStyleSheet(TITLE_2_TEXT)
        self.title.setContentsMargins(0, 0, 0, 15)

        self.tel_temp = QLabel("TEMP: -- °C")
        self.tel_temp.setStyleSheet(TEXT_BOLD)
        
        self.tel_cpu = QLabel("CPU: -- %")
        self.tel_cpu.setStyleSheet(TEXT_BOLD)

        self.tel_ram = QLabel("RAM: -- %")
        self.tel_ram.setStyleSheet(TEXT_BOLD)
        
        self.tel_warn = QLabel("")
        self.tel_warn.setStyleSheet(ALERT_TEXT)

        layout.addWidget(self.title)
        layout.addWidget(self.tel_temp)
        layout.addWidget(self.tel_cpu)
        layout.addWidget(self.tel_ram)
        layout.addWidget(self.tel_warn)

        self.telemetry_received.connect(self.update_telemetry_ui)

    def update_telemetry(self, data):
        self.telemetry_received.emit(data)

    def update_telemetry_ui(self, data):
        """ Triggered automatically by the network listener """
        self.tel_temp.setText(f"TEMP: {data['cpu_temp']} °C")
        self.tel_cpu.setText(f"CPU: {data['cpu_usage']} %")
        self.tel_ram.setText(f"RAM: {data['ram_usage']} %")
        
        # Flash the temp red if it gets dangerously hot (over 75C)
        if data['cpu_temp'] > 75.0:
            self.tel_temp.setText(f"⚠️ TEMP: {data['cpu_temp']} °C")
            self.tel_temp.setStyleSheet(ALERT_TEXT)
        else:
            self.tel_temp.setStyleSheet(TEXT_BOLD)
            
        if data['low_power']:
            self.tel_warn.setText("⚠️ LOW VOLTAGE! ")
        else:
            self.tel_warn.setText("")