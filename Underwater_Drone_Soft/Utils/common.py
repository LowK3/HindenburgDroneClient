import sys
import time
from config import LOG_PREFIX

def log(msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"{LOG_PREFIX} {ts} | {msg}")
    sys.stdout.flush()

def recv_all(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionResetError("Socket closed.")
        data += chunk
    return data