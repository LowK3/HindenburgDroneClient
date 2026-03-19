import socket, traceback, json
from config import CONTROL_TCP_PORT, CONTROL_TIMEOUT
from Utils.logger import log

class ControlClient:
    """ Client-side engine control link. """
    def __init__(self):
        self.sock = None

    def connect(self, ip):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(CONTROL_TIMEOUT)
        try:
            self.sock.connect((ip, CONTROL_TCP_PORT))
            self.sock.settimeout(None)
            log(f"Control TCP connected to {ip}:{CONTROL_TCP_PORT}.")
            return True
        except Exception as e:
            log(f"Control TCP connection failed: {e}\n{traceback.format_exc()}")
            self.sock = None
            return False

    def send(self, payload: dict):
        if not self.sock:
            return
        try:
            data_str = json.dumps(payload) + "\n"
            self.sock.sendall(data_str.encode())
        except Exception as e:
            log(f"Control send error: {e}\n{traceback.format_exc()}")
            self.sock = None

    def stop(self):
        if self.sock:
            self.sock.close()
            log("Control TCP socket closed.")
        self.sock = None
