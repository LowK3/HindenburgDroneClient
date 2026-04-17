from PySide6.QtGui import QPixmap, QPainter

def recv_all(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionResetError("Socket closed.")
        data += chunk
    return data

def preload_emojis():
    pixmap = QPixmap(1, 1)
    painter = QPainter(pixmap)
    painter.drawText(0, 0, "⚠️")
    painter.end()
