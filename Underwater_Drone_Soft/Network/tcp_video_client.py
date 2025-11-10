import socket, struct, cv2, numpy as np, time
from config import TCP_TIMEOUT, TCP_RECV_TIMEOUT, DATA_WAIT
from Utils.common import log, recv_all

class TCPClient:
    """Maintains TCP connection to server and receives JPEG frames."""
    def __init__(self):
        self.sock = None
        self.last_data_time = 0

    def connect(self, ip, port):
        self.stop()
        log(f"Connecting to TCP server {ip}:{port} ...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
        self.sock.settimeout(TCP_TIMEOUT)
        try:
            self.sock.connect((ip, port))
            self.sock.settimeout(TCP_RECV_TIMEOUT)
            self.last_data_time = time.time()
            log("TCP connection established")
            return True
        except Exception as e:
            log(f"TCP connect failed: {e}")
            self.stop()
            return False

    def receive_frame(self):
        """Receive one length-prefixed frame, returns np.array or None."""
        if not self.sock:
            raise ConnectionError("Socket not connected")

        try:
            header = recv_all(self.sock, 4)
            frame_len = struct.unpack("<I", header)[0]
            if frame_len <= 0 or frame_len > 10_000_000:
                raise ValueError(f"Invalid frame length {frame_len}")
            data = recv_all(self.sock, frame_len)
            self.last_data_time = time.time()
            np_img = np.frombuffer(data, dtype=np.uint8)
            return cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        except socket.timeout:
            if time.time() - self.last_data_time > DATA_WAIT:
                raise TimeoutError("No data from server")
            return None
        except Exception as e:
            raise ConnectionResetError(f"TCP receive error: {e}")

    def is_alive(self):
        return self.sock is not None and (time.time() - self.last_data_time < DATA_WAIT)

    def stop(self):
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.sock.close()
                log("TCP socket closed")
            except Exception as e:
                log(f"Error closing TCP socket: {e}")
        self.sock = None
        time.sleep(1.0)  # give OS time to recycle port
