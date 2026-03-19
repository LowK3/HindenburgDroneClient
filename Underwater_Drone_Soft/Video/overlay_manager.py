from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QStackedLayout, QLabel, 
    QPushButton, QGraphicsBlurEffect
)
from PySide6.QtCore import Qt
from Video.main_menu_widget import MainMenuWidget
from Video.settings_widget import SettingsWidget
from Video.info_widget import InfoWidget
from Video.tutorial_widget import TutorialWidget
from Video.confirm_widget import ConfirmWidget
from Utils.logger import log, open_logs_file
from Video.styles import MAIN_PANEL_STYLE, TITLE_TEXT, MENU_BTN_STYLE

class OverlayManager(QWidget):
    """ Handles all menus, popups, and screen blurring for the main window """
    def __init__(self, main_window):
        super().__init__(main_window.centralWidget())
        self.main = main_window
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setObjectName("BaseOverlay")
        self.setStyleSheet("#BaseOverlay { background-color: rgba(40, 40, 40, 180); }")
        
        self.overlay_stack = QStackedLayout(self)
        self._build_ui()
        self.hide()

    def _build_ui(self):
        # PAGE 0: MAIN MENU
        self.main_menu_widget = MainMenuWidget(self)
        self.main_menu_widget.resume_clicked.connect(self.toggle_menu)
        self.main_menu_widget.settings_clicked.connect(lambda: self.overlay_stack.setCurrentIndex(1))
        self.main_menu_widget.logs_clicked.connect(open_logs_file)
        self.main_menu_widget.quit_clicked.connect(self.main.close)

        # Page 1: SETTINGS MENU
        self.settings_page = SettingsWidget(self.main.input.bindings, self.main)
        self.settings_page.save_clicked.connect(self.save_and_return)

        # Page 2: INFO MENU
        self.info_page = InfoWidget(self.main)
        self.info_page.close_clicked.connect(self.close_info_page)
        self.info_page.tutorial_clicked.connect(lambda: self.overlay_stack.setCurrentIndex(3))

        # Page 3: TUTORIAL MENU
        self.tutorial_page = TutorialWidget(self.main)
        self.tutorial_page.back_clicked.connect(lambda: self.overlay_stack.setCurrentIndex(2))

        self.overlay_stack.addWidget(self.main_menu_widget)
        self.overlay_stack.addWidget(self.settings_page)
        self.overlay_stack.addWidget(self.info_page)
        self.overlay_stack.addWidget(self.tutorial_page)

        # Overlay: CONFIRMATION POPUP
        self.confirm_overlay = ConfirmWidget(self)
        self.confirm_overlay.hide()
        self.confirm_overlay.accepted.connect(self.confirm_save_yes)
        self.confirm_overlay.rejected.connect(self.confirm_save_no)

    # --- BACKGROUND BLUR EFFECTS ---
    def _apply_background_blur(self):
        """ Blurs the entire video layer (feed, HUD, and buttons). """
        blur_effect = QGraphicsBlurEffect(self.main.video_container)
        blur_effect.setBlurRadius(10)
        self.main.video_container.setGraphicsEffect(blur_effect)

    def _remove_background_blur(self):
        self.main.video_container.setGraphicsEffect(None)

    # --- VISIBILITY & LOGIC ---
    def toggle_menu(self):
        if self.isVisible():
            if self.confirm_overlay.isVisible():
                self.confirm_overlay.hide()
                return

            current_idx = self.overlay_stack.currentIndex()
            if current_idx == 1:
                if self.settings_page.has_unsaved_changes():
                    self.confirm_overlay.setGeometry(self.rect())
                    self.confirm_overlay.show()
                    self.confirm_overlay.raise_()
                    return
                else:
                    self.overlay_stack.setCurrentIndex(0)
            elif current_idx == 2:
                self.close_info_page()
            elif current_idx == 3:
                self.overlay_stack.setCurrentIndex(2)
            else:
                self.main.video_container.setGraphicsEffect(None)
                self.hide()
                self.overlay_stack.setCurrentIndex(0)
                self.main.setFocus()
        else:
            self.setGeometry(self.main.centralWidget().rect())
            self._apply_background_blur()
            self.show()
            self.raise_()
            self.main.setFocus()

    def resize_overlays(self, rect):
        """ Keeps the overlays perfectly sized with the main window """
        self.setGeometry(rect)
        if self.confirm_overlay.isVisible():
            self.confirm_overlay.setGeometry(self.rect())

    def show_info_page(self):
        show_info = self.main.input.settings.value("show_info_on_startup", True, type=bool)
        self.info_page.dont_show_cb.setChecked(not show_info)

        if not self.isVisible():
            self.setGeometry(self.main.centralWidget().rect())
            self._apply_background_blur()
            self.show()
            self.raise_()
        self.overlay_stack.setCurrentIndex(2)

    def close_info_page(self):
        dont_show = self.info_page.dont_show_cb.isChecked()
        self.main.input.settings.setValue("show_info_on_startup", not dont_show)
        self.main.video_container.setGraphicsEffect(None)
        self._remove_background_blur()
        self.hide()
        self.overlay_stack.setCurrentIndex(0)

    def save_and_return(self):
        new_bindings = self.settings_page.get_new_bindings()
        self.main.input.save_bindings(new_bindings)
        self.overlay_stack.setCurrentIndex(0)
        log("New keybinds saved successfully.")

    def confirm_save_yes(self):
        self.save_and_return()
        self.confirm_overlay.hide()
        
    def confirm_save_no(self):
        self.settings_page.revert_changes()
        self.overlay_stack.setCurrentIndex(0)
        self.confirm_overlay.hide()