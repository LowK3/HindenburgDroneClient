import sys, time, logging, os
from logging.handlers import RotatingFileHandler
from config import LOG_PREFIX

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "system.log")

logger = logging.getLogger("DroneLogger")
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    LOG_FILE, 
    maxBytes = 5 * 1024 * 1024, 
    backupCount = 2
)

formatter = logging.Formatter("[CLIENT] [%(asctime)s] | %(message)s", datefmt="%H:%M:%S")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def log(msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"{LOG_PREFIX} {ts} | {msg}")
    logger.info(msg)

def recv_all(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionResetError("Socket closed.")
        data += chunk
    return data