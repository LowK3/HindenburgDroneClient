PANEL_BG_COLOR ="#1A1A1A"

BTN_BG_COLOR = "#333"
BTN_HOVER_COLOR = "#444444"
BORDER_COLOR = "#444"
BORDER_HOVER_COLOR = "#666"

UNBOUND_COLOR = "#cc0000"
UNBOUND_HOVER_COLOR = "#FF3336"
BORDER_UNBOUND_COLOR = "#FF3336"
BORDER_UNBOUND_HOVER_COLOR= "#FF6669"

PRESS_KEY_COLOR = "#DBDBDB"

ACCENT_GREEN = "#33FF33"
ACCENT_RED = "#FF3333"

TEXT_WHITE = "white"
FONT_FAMILY = "'Segoe UI'"

def get_status_dot_style(connected):
    color = f"{ACCENT_GREEN}" if connected else f"{ACCENT_RED   }"
    return f"background-color: {color}; border-radius: 6px;"

TEXT_STYLE = f"""
    font-family: {FONT_FAMILY};
    color: {TEXT_WHITE};
"""

WAITING_TITLE = f"""
    font-family: {FONT_FAMILY};
    font-size: 48px;
    font-weight: bold;
    color: {TEXT_WHITE};
"""

TITLE_TEXT = f"""
    font-family: {FONT_FAMILY};
    font-size: 32px;
    font-weight: bold;
    color: {TEXT_WHITE};
    margin-bottom: 20px;
"""

TITLE_2_TEXT = f"""
    font-family: {FONT_FAMILY};
    font-size: 20px;
    font-weight: bold;
    color: {TEXT_WHITE};
"""

TEXT = f"""
    font-family: {FONT_FAMILY};
    font-size: 17px;
    color: {TEXT_WHITE};
"""

TEXT_BOLD = f"""
    {TEXT}
    font-weight: bold;
"""

MAIN_PANEL_STYLE = f"""
    #MainPanel, #SettingsPanel, #InfoPanel, #TutorialPanel, #ConfirmPanel {{
        background-color: {PANEL_BG_COLOR};
        border-radius: 15px;
        border: 2px solid {BORDER_COLOR};
    }}
    QLabel {{
        border: none;
        background: transparent;
    }}
    QCheckBox {{
        border: none;
        background: transparent;
    }}
    QScrollArea, QScrollArea > QWidget > QWidget {{
        border: none;
        background: transparent;
    }}
    QFrame {{
        border: none;
    }}
"""

CHECKBOX_STYLE = f"""
    QCheckBox {{
        font-family: {FONT_FAMILY};
        color: {TEXT_WHITE}; 
        font-size: 14px; 
        background: transparent; 
    }}
    QCheckBox::indicator {{
        border: 2px solid {BORDER_COLOR}; 
        border-radius: 5px;
        width: 16px; 
        height: 16px; 
    }}
    QCheckBox::indicator:checked {{
        background-color: white;
        border-radius: 5px;
    }}
"""

MENU_BTN_STYLE = f"""
    QPushButton {{
        font-family: {FONT_FAMILY};
        background-color: {BTN_BG_COLOR};
        color: {TEXT_WHITE};
        border: 2px solid {BORDER_COLOR};
        border-radius: 5px;
        font-size: 20px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {BTN_HOVER_COLOR};
        border: 2px solid {BORDER_HOVER_COLOR};
    }}
"""

BTN_STYLE = f"""
    QPushButton {{
        font-family: {FONT_FAMILY};
        background-color: {BTN_BG_COLOR};
        color: {TEXT_WHITE};
        border: 2px solid {BORDER_COLOR};
        border-radius: 5px;
        font-size: 18px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {BTN_HOVER_COLOR};
        border: 2px solid {BORDER_HOVER_COLOR};
    }}
"""

GREEN_BTN_STYLE = f"""
    QPushButton {{
        font-family: {FONT_FAMILY};
        background-color: #33FF33;
        color: black;
        border: 2px solid #22CC22;
        border-radius: 5px;
        font-size: 18px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: #5EFF55;
        border: 2px solid #1D911C;
    }}
"""

INFO_BTN_STYLE = f"""
    QPushButton {{
        font-family: {FONT_FAMILY};
        background-color: {BTN_BG_COLOR};
        color: {TEXT_WHITE};
        border: 1px solid {BORDER_COLOR};
        border-radius: 5px;
        font-size: 16px;
        font-weight: bold;
        margin: 10px;
    }}
    QPushButton:hover {{
            background-color: {BTN_HOVER_COLOR};
            border: 1px solid {BORDER_HOVER_COLOR};
    }}
"""

SMALL_BTN_STYLE = f"""
    QPushButton {{
        background-color: {BTN_BG_COLOR};
        color: {TEXT_WHITE};
        border: 1px solid {BORDER_COLOR};
        border-radius: 5px;
        padding: 5px;
    }}
    QPushButton:hover {{
        background-color: {BTN_HOVER_COLOR};
        border: 1px solid {BORDER_HOVER_COLOR};
    }}
"""

UNBOUND_BTN_STYLE = f"""
    QPushButton {{
        background-color: {UNBOUND_COLOR};
        color: {TEXT_WHITE};
        border: 1px solid {BORDER_UNBOUND_COLOR};
        border-radius: 5px;
        padding: 5px;
    }}
    QPushButton:hover {{
        background-color: {UNBOUND_HOVER_COLOR};
        border: 1px solid {BORDER_UNBOUND_HOVER_COLOR};
    }}
"""

PRESS_KEY_STYLE = f"""
    font-family: {FONT_FAMILY};
    background-color: {PRESS_KEY_COLOR};
    color: black;
    border: 1px solid {BORDER_COLOR};
    border-radius: 5px;
    padding: 5px;
"""

SCROLL_AREA_STYLE = f"""
    QScrollArea {{
        border: none; background: transparent; 
    }}
    QScrollBar:vertical {{
        border: none; background: transparent; width: 10px; margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {BTN_BG_COLOR}; min-height: 25px; border: 1px solid {BORDER_COLOR}; 
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {BTN_HOVER_COLOR}; border: 1px solid {BORDER_HOVER_COLOR};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none; background: none; height: 0px;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}
"""

CONNECTION_PANEL_STYLE = f"""
    QWidget {{
        background-color: {BTN_BG_COLOR}; border: 1px solid {BORDER_COLOR};
        border-radius: 5px; margin: 10px;
    }}
    QLabel {{
        font-family: {FONT_FAMILY};
        color: {TEXT_WHITE};
        font-size: 14px;
        font-weight: bold;
        border: none;
        margin-left: 0px; 
        margin-right: 0px;
    }}
    QLabel#StatusDot {{
        min-width: 14px; min-height: 14px;
        max-width: 14px; max-height: 14px;
        border-radius: 6px;
    }}
"""