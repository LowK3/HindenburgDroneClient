import socket, traceback, json, threading
from PySide6.QtCore import QObject, Signal
from config import CONTROL_TCP_PORT, CONTROL_TIMEOUT, TIMEOUT
from Utils.logger import log

class ControlClient(QObject):
    """ Client-side engine control link. """
    telemetry_received = Signal(dict)

    def __init__(self):
        super().__init__()
        self.sock = None
        self._stop_event = threading.Event()

    def connect(self, ip):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(CONTROL_TIMEOUT)
        try:
            self.sock.connect((ip, CONTROL_TCP_PORT))
            self.sock.settimeout(None)
            log(f"Control TCP connected to {ip}:{CONTROL_TCP_PORT}.")

            self._stop_event.clear()
            threading.Thread(target=self.receive, daemon=True).start()

            return True
        except Exception as e:
            log(f"Control TCP connection failed: {e}\n{traceback.format_exc()}")
            self.sock = None
            return False

    def is_connected(self) -> bool:
        return self.sock is not None

    def send(self, payload: dict):
        if not self.is_connected():
            return
        try:
            data_str = json.dumps(payload) + "\n"
            self.sock.sendall(data_str.encode())
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            log("Control TCP disconnected by server.")
            self.stop()
        except Exception as e:
            log(f"Control send error: {e}\n{traceback.format_exc()}")
            self.stop()

    def receive(self):
        """ Background thread that catches telemetry from the server """
        buffer = bytearray()
        while not self._stop_event.is_set() and self.is_connected():
            try:
                self.sock.settimeout(TIMEOUT)
                data = self.sock.recv(1024)
                if not data:
                    break
                buffer.extend(data)
                
                while (newline_idx := buffer.find(b"\n")) != -1:
                    msg_bytes = buffer[:newline_idx]
                    del buffer[:newline_idx + 1]
                    if msg_bytes:
                        try:
                            msg_str = msg_bytes.decode('utf-8').strip()
                            payload = json.loads(msg_str)
                            if payload.get("type") == "TELEMETRY":
                                self.telemetry_received.emit(payload)
                        except (UnicodeDecodeError, json.JSONDecodeError):
                            pass
            except socket.timeout:
                continue
            except (OSError, ConnectionAbortedError, ConnectionResetError):
                # Socket closed intentionally by stop() or disconnected by server
                break
            except Exception as e:
                log(f"Fatal error in receive thread: {e}\n{traceback.format_exc()}")
                break

    def stop(self):
        self._stop_event.set()
        if self.is_connected():
            self.sock.close()
            log("Control TCP socket closed.")
        self.sock = None
