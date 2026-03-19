from PySide6.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QLabel, QFormLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence
from Video.styles import (
    MAIN_PANEL_STYLE, TITLE_TEXT, TEXT, BTN_STYLE, SMALL_BTN_STYLE, 
    UNBOUND_BTN_STYLE, PRESS_KEY_STYLE
)

CMD_LABELS = {
    "W": "FORWARD", "S": "BACKWARD", "A": "TURN LEFT", "D": "TURN RIGHT",
    "UP": "TILT UP", "DOWN": "TILT DOWN",
    "REAR+": "REAR POWER +", "REAR-": "REAR POWER -",
    "FRONT+": "FRONT POWER +", "FRONT-": "FRONT POWER -"
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
            self.setStyleSheet(UNBOUND_BTN_STYLE)
        else:
            self.setText(QKeySequence(self.current_key).toString())
            self.setStyleSheet(SMALL_BTN_STYLE)

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
            self.setStyleSheet(PRESS_KEY_STYLE)
            self.setFocus()

class SettingsWidget(QWidget):
    """ The in-overlay settings page for changing keybinds. """
    save_clicked = Signal()

    def __init__(self, current_bindings, parent=None):
        super().__init__(parent)
        self.bindings = current_bindings.copy()
        self.buttons = {}
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignCenter)
        
        self.panel = QWidget()
        self.panel.setObjectName("SettingsPanel")
        self.panel.setStyleSheet(MAIN_PANEL_STYLE)
        self.panel.setFixedWidth(450)
        
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setAlignment(Qt.AlignCenter)
        panel_layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("CONTROL SETTINGS")
        title.setStyleSheet(TITLE_TEXT)
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
            lbl.setStyleSheet(TEXT)
            form_layout.addRow(lbl, btn)
            
        panel_layout.addWidget(form_container)
        
        panel_layout.addSpacing(30)
        self.save_btn = QPushButton("SAVE | RETURN")
        self.save_btn.setFixedHeight(50)
        self.save_btn.setStyleSheet(BTN_STYLE)
        panel_layout.addWidget(self.save_btn)
        outer_layout.addWidget(self.panel)

        self.save_btn.clicked.connect(self.save_clicked.emit)

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
        self.reset_all_grabbers()
        for cmd, btn in self.buttons.items():
            self.bindings[cmd] = btn.current_key
        return self.bindings

    def has_unsaved_changes(self):
        self.reset_all_grabbers()
        for cmd, btn in self.buttons.items():
            if self.bindings[cmd] != btn.current_key:
                return True
        return False

    def revert_changes(self):
        self.reset_all_grabbers()
        for cmd, btn in self.buttons.items():
            btn.current_key = self.bindings[cmd]
            btn.update_display()