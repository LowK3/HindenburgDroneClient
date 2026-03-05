from PySide6.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QLabel, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence

CMD_LABELS = {
    "W\n": "FORWARD", "S\n": "BACKWARD", "A\n": "TURN LEFT", "D\n": "TURN RIGHT",
    "UP\n": "TILT UP", "DOWN\n": "TILT DOWN",
    "REAR+\n": "REAR POWER +", "REAR-\n": "REAR POWER -",
    "FRONT+\n": "FRONT POWER +", "FRONT-\n": "FRONT POWER -"
}

class KeyGrabberButton(QPushButton):
    """ A button that listens for a keypress and saves it. """
    def __init__(self, cmd, current_key, parent_menu):
        super().__init__(parent_menu)
        self.cmd = cmd
        self.current_key = current_key
        self.parent_menu = parent_menu
        self.listening = False
        self.update_display()

    def update_display(self):
        if self.current_key == 0:
            self.setText("UNBOUND")
            self.setStyleSheet("""
            font-family: 'Segoe Ui'; background-color: #cc0000; 
            color: white; padding: 5px; border-radius: 5px;
            border: 1px solid #FF3336
            """)
        else:
            self.setText(QKeySequence(self.current_key).toString())
            self.setStyleSheet("""
            font-family: 'Segoe Ui'; background-color: #333; 
            color: white; padding: 5px; border-radius: 5px;
            border: 1px solid #444
            """)

    def keyPressEvent(self, event):
        if self.listening:
            key = event.key()
            if key == Qt.Key_Escape:
                self.listening = False
                self.clearFocus()
                self.update_display()
                return
            
            self.parent_menu.resolve_key_conflict(self.cmd, key)
            self.listening = False
            self.clearFocus()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        was_listening = self.listening
        self.parent_menu.reset_all_grabbers()

        if not was_listening:
            self.listening = True
            self.setText("PRESS ANY KEY...")
            self.setStyleSheet("""
            font-family: 'Segoe Ui'; background-color: #DBDBDB; 
            color: black; padding: 5px; border-radius: 5px;
            border: 1px solid #444
            """)
            self.setFocus()

class SettingsWidget(QWidget):
    """ The in-overlay settings page for changing keybinds. """
    def __init__(self, current_bindings, parent=None):
        super().__init__(parent)
        self.bindings = current_bindings.copy()
        self.buttons = {}
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignCenter)
        
        self.panel = QWidget()
        self.panel.setObjectName("SolidPanel")
        self.panel.setStyleSheet("#SolidPanel { background-color: #1A1A1A; border-radius: 15px; border: 2px solid #333; }")
        self.panel.setFixedWidth(450)
        
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setAlignment(Qt.AlignCenter)
        panel_layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("CONTROL SETTINGS")
        title.setStyleSheet("""
        font-family: 'Segoe Ui'; font-size: 32px; font-weight: bold;
        color: white; margin-bottom: 20px; background: transparent;
        """)
        title.setAlignment(Qt.AlignCenter)
        panel_layout.addWidget(title)
        
        form_container = QWidget()
        form_container.setStyleSheet("background-color: transparent; border: none;")
        form_layout = QFormLayout(form_container)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setSpacing(15)
        
        for cmd, key in self.bindings.items():
            btn = KeyGrabberButton(cmd, key, self)
            self.buttons[cmd] = btn
            
            lbl = QLabel(CMD_LABELS[cmd] + "   ")
            lbl.setStyleSheet("""
            font-family: 'Segoe Ui'; font-size: 17px; 
            color: white; background: transparent;
            """)
            form_layout.addRow(lbl, btn)
            
        panel_layout.addWidget(form_container)
        
        self.save_btn = QPushButton("SAVE | RETURN")
        self.save_btn.setFixedHeight(50)
        self.save_btn.setStyleSheet("""
            QPushButton {
                font-family: 'Segoe Ui'; background-color: #333; color: white;
                border: 2px solid #444; border-radius: 5px;
                font-size: 18px; font-weight: bold; margin-top: 20px;
            }
            QPushButton:hover { background-color: #444444; border: 2px solid #666; }
        """)
        panel_layout.addWidget(self.save_btn)
        outer_layout.addWidget(self.panel)

    def reset_all_grabbers(self):
        for btn in self.buttons.values():
            if btn.listening:
                btn.listening = False
                btn.clearFocus()
                btn.update_display()

    def resolve_key_conflict(self, target_cmd, new_key):
        for cmd, btn in self.buttons.items():
            if btn.current_key == new_key and cmd != target_cmd:
                btn.current_key = 0 
                btn.update_display()
                
        target_btn = self.buttons[target_cmd]
        target_btn.current_key = new_key
        target_btn.update_display()

    def get_new_bindings(self):
        for cmd, btn in self.buttons.items():
            self.bindings[cmd] = btn.current_key
        return self.bindings