import cv2
import numpy as np
from PySide6.QtGui import QImage, QPixmap

def create_qpixmap(frame: np.ndarray, target_width: int, target_height: int):
    """ Resizes frame to fit within target dimensions and convert it to a PySide6 QPixmap. """
    frame_h, frame_w, _ = frame.shape
    scale = min(target_width / frame_w, target_height / frame_h)
    new_w = int(frame_w * scale)
    new_h = int(frame_h * scale)

    frame_resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    qt_img = QImage(frame_resized.data, new_w, new_h, 3 * new_w, QImage.Format_BGR888)
    return QPixmap.fromImage(qt_img)