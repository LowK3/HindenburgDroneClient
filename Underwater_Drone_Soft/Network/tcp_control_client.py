import socket, traceback, json, threading
from config import CONTROL_TCP_PORT, CONTROL_TIMEOUT, TIMEOUT
from Utils.logger import log

class ControlClient:
    """ Client-side engine control link. """
    def __init__(self):
        self.sock = None
        self.telemetry_callback = None
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

    def send(self, payload: dict):
        if not self.sock:
            return
        try:
            data_str = json.dumps(payload) + "\n"
            self.sock.sendall(data_str.encode())
        except Exception as e:
            log(f"Control send error: {e}\n{traceback.format_exc()}")
            self.sock = None

    def receive(self):
        """ Background thread that catches telemetry from the server """
        buffer = ""
        while not self._stop_event.is_set() and self.sock:
            try:
                self.sock.settimeout(TIMEOUT)
                data = self.sock.recv(1024)
                if not data:
                    break
                buffer += data.decode()
                
                while "\n" in buffer:
                    msg, buffer = buffer.split("\n", 1)
                    if msg and self.telemetry_callback:
                        try:
                            payload = json.loads(msg)
                            if payload.get("type") == "TELEMETRY":
                                self.telemetry_callback(payload)
                        except json.JSONDecodeError:
                            pass
            except socket.timeout:
                continue
            except Exception:
                break

    def stop(self):
        self._stop_event.set()
        if self.sock:
            self.sock.close()
            log("Control TCP socket closed.")
        self.sock = None
