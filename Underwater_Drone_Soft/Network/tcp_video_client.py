import socket, struct, cv2, numpy as np
from Utils.common import recv_all
from config import TCP_TIMEOUT, DATA_WAIT

class TCPClient:
    def __init__(self):
        self.sock = None

    def connect(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(TCP_TIMEOUT)
        self.sock.connect((ip, port))
        self.sock.settimeout(None)

    def receive_frame(self):
        header = recv_all(self.sock, 4)
        frame_len = struct.unpack("<I", header)[0]
        data = recv_all(self.sock, frame_len)
        np_img = np.frombuffer(data, dtype=np.uint8)
        return cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
