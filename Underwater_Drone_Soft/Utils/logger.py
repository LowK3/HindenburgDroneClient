import sys
import time
import logging
import os
import traceback
import platform
import subprocess
from logging.handlers import RotatingFileHandler
from config import LOG_PREFIX

logger = logging.getLogger("DroneClient")

def setup_logging():
    LOG_DIR = "logs"
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    LOG_FILE = os.path.join(LOG_DIR, "system.log")
    logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=2)
    formatter = logging.Formatter("[CLIENT] [%(asctime)s] | %(message)s", datefmt="%H:%M:%S")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def log(msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"{LOG_PREFIX} {ts} | {msg}")
    logger.info(msg)

def open_logs_file():
    """ Generates a reversed log file on demand and opens it in the default text editor. """
    log_dir = "logs"
    source_file = os.path.join(log_dir, "system.log")
    reversed_file = os.path.join(log_dir, "system_reversed.log")

    if not os.path.exists(source_file):
        log("Cannot open logs: system.log does not exist yet.")
        return

    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        with open(reversed_file, 'w', encoding='utf-8') as f:
            f.writelines(reversed(lines))

        if platform.system() == 'Windows':
            os.startfile(reversed_file)
    except Exception as e:
        log(f"Failed to open reversed log: {e}\n{traceback.format_exc()}")

def global_crash_handler(exc_type, exc_value, exc_tb):
    """ Catches any fatal crash in the app and saves it to the log file. """
    # Ignore normal manual shutdowns (like pressing Ctrl+C)
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
        
    crash_report = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    log(f"CRITICAL APP CRASH:\n{crash_report}")

sys.excepthook = global_crash_handler