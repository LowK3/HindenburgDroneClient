from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath
from PySide6.QtCore import Qt
from Video.styles import RETICLE_YELLOW, RETICLE_GREEN, RETICLE_D_GREY, RETICLE_L_GREY

class ArtificialHorizon(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(250, 250)
        self.pitch = 0.0
        self.roll = 0.0

    def update_angles(self, pitch, roll):
        self.pitch = max(-120.0, min(120.0, pitch))
        self.roll = roll
        self.update() 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(RETICLE_D_GREY))
        painter.drawEllipse(0, 0, width, height)

        # Set clipping mask so moving lines don't bleed out of the circle
        clip_path = QPainterPath()
        clip_path.addEllipse(0, 0, width, height)
        painter.setClipPath(clip_path)

        # Save origin state
        painter.save()
        painter.translate(center_x, center_y)

        # Apply Roll and Pitch transformations
        painter.rotate(-self.roll)
        pitch_pixels = self.pitch * 4.0  # Scale: 4 pixels per degree of pitch
        painter.translate(0, pitch_pixels)

        # Draw the Horizon Line
        painter.setPen(QPen(QColor(RETICLE_GREEN), 2))
        painter.drawLine(-width, 0, width, 0)

        # Draw the Pitch Ladder
        painter.setPen(QPen(QColor(RETICLE_L_GREY), 1))
        font = painter.font()
        font.setPixelSize(15)
        font.setBold(True)
        painter.setFont(font)
        for i in range(-36, 37):
            if i == 0: continue

            # i represents 5 degrees. At 3 pixels per degree, y_pos shifts by 20.
            y_pos = i * 20
            if i % 2 == 0:
                # Major lines (10, 20, 30 degrees)
                line_width = 30
                painter.drawLine(-line_width, y_pos, line_width, y_pos)
                
                # Calculate and draw the text
                pitch_val = -i * 5 
                painter.drawText(-line_width - 30, y_pos + 4, str(pitch_val))
                painter.drawText(line_width + 8, y_pos + 4, str(pitch_val))
            else:
                # Minor lines (5, 15, 25 degrees)
                line_width = 15
                painter.drawLine(-line_width, y_pos, line_width, y_pos)

        # Restore origin to draw the fixed submarine reticle
        painter.restore()
        painter.translate(center_x, center_y)

        # Draw Fixed Submarine Reticle (Yellow)
        painter.setPen(QPen(QColor(RETICLE_YELLOW), 3))
        # Center dot
        painter.drawPoint(0, 0)
        # Left strut
        painter.drawLine(-60, 0, -25, 0)
        painter.drawLine(-60, 0, -60, 15)
        # Right strut
        painter.drawLine(25, 0, 60, 0)
        painter.drawLine(60, 0, 60, 15)
        # Top fin
        painter.drawLine(0, -25, 0, -40)

        painter.end()