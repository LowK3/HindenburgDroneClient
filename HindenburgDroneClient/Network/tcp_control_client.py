import socket
import traceback
import json
import threading
from PySide6.QtCore import QObject, Signal
from config import (
    CONTROL_TCP_PORT, TCP_CONNECT_TIMEOUT, TCP_RECV_TIMEOUT, TCP_RECV_CHUNK,
    TCP_BUFFER_SIZE, TELEMETRY_PACKET_TYPES
)
from Utils.logger import log

class ControlClient(QObject):
    """ Client-side engine control link. """
    telemetry_received = Signal(dict)

    def __init__(self):
        super().__init__()
        self.sock = None
        self._stop_event = threading.Event()

        self.telemetry_state = {
            "pitch": 0.0,
            "roll": 0.0,
            "front_pwr": None,
            "rear_pwr": None,
            "leak_detected": False,
            "cpu_temp": None,
            "cpu_usg": None,
            "ram_usg": None,
            "low_pwr": None,
            "hull_temp": None,
            "hull_hum": None,
            "hull_press": None,
            "camera_status": True
        }

    def connect(self, ip: str):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Disable Nagle's Algorithm to prevent artificial latency
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.settimeout(TCP_CONNECT_TIMEOUT)
        try:
            self.sock.connect((ip, CONTROL_TCP_PORT))
            self.sock.settimeout(None)
            log(f"Control TCP connected to {ip}:{CONTROL_TCP_PORT}.")

            self._reset_telemetry_state()
            self._stop_event.clear()
            threading.Thread(target=self._receive, daemon=True).start()

            return True
        except Exception as e:
            log(f"Control TCP connection failed: {e}\n{traceback.format_exc()}")
            self.sock.close()
            self.sock = None
            return False

    def is_connected(self):
        return self.sock is not None

    def send(self, payload: dict):
        if not self.is_connected():
            return
        try:
            data_str = json.dumps(payload).encode("utf-8") + b"\n"
            self.sock.sendall(data_str)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            log("Control TCP disconnected by server.")
            self.stop()
        except Exception as e:
            log(f"Control send error: {e}\n{traceback.format_exc()}")
            self.stop()

    def _receive(self):
        """ Background thread that catches telemetry from the server """
        buffer = bytearray()
        sock = self.sock
        sock.settimeout(TCP_RECV_TIMEOUT)

        while not self._stop_event.is_set() and self.is_connected():
            try:
                data = sock.recv(TCP_RECV_CHUNK)
                if not data:
                    break
                buffer.extend(data)
                self._process_buffer(buffer)

                if len(buffer) > TCP_BUFFER_SIZE:
                    log("WARNING! TCP receive buffer overflow. Clearing buffer.")
                    buffer.clear()
            except socket.timeout:
                continue
            except (OSError, ConnectionAbortedError, ConnectionResetError):
                # Socket closed intentionally by stop() or disconnected by server
                break
            except Exception as e:
                log(f"Fatal error in receive thread: {e}\n{traceback.format_exc()}")
                break

        if not self._stop_event.is_set():
            log("Control TCP connection lost.")
            self.stop()

    def _process_buffer(self, buffer: bytearray):
        while (newline_idx := buffer.find(b"\n")) != -1:
            msg_bytes = buffer[:newline_idx]
            del buffer[:newline_idx + 1]
            if msg_bytes:
                self._decode_and_emit(msg_bytes)

    def _decode_and_emit(self, msg_bytes: bytes):
        try:
            msg_str = msg_bytes.decode("utf-8").strip()
            payload = json.loads(msg_str)
            if not isinstance(payload, dict):
                return

            packet_type = payload.get("type")
            if packet_type not in TELEMETRY_PACKET_TYPES:
                return

            self.telemetry_state.update(payload)
            self.telemetry_received.emit(self.telemetry_state.copy())
        except (UnicodeDecodeError, json.JSONDecodeError):
            pass

    def _reset_telemetry_state(self):
        self.telemetry_state = {
            "pitch": 0.0,
            "roll": 0.0,
            "front_pwr": None,
            "rear_pwr": None,
            "leak_detected": False,
            "cpu_temp": None,
            "cpu_usg": None,
            "ram_usg": None,
            "low_pwr": None,
            "hull_temp": None,
            "hull_hum": None,
            "hull_press": None,
            "camera_status": True
        }

    def stop(self):
        self._stop_event.set()
        if self.is_connected():
            self.sock.close()
            log("Control TCP socket closed.")
        self.sock = None
