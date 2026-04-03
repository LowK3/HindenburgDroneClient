import sys
import threading
from PySide6.QtWidgets import QApplication
from Video.gui import VideoWindow
from Utils.frame_buffer import FrameBuffer
from Network.network_worker import NetworkWorker
from config import NETWORK_JOIN_TIMEOUT
from Utils.logger import log, setup_logging

class ClientApp:
    def __init__(self):
        self.fb = FrameBuffer()
        self._stop_event = threading.Event()

    def run(self):
        setup_logging()

        # Start networking thread
        net = NetworkWorker(self.fb, self._stop_event)
        net_thread = threading.Thread(target=net.run, daemon=True)
        net_thread.start()

        # Start Qt GUI
        app = QApplication(sys.argv)
        window = VideoWindow(self.fb, net.control)

        exit_code = app.exec()

        # Shutdown
        log("GUI closed, stopping network.")
        self._stop_event.set()
        net_thread.join(timeout=NETWORK_JOIN_TIMEOUT)

        sys.exit(exit_code)

if __name__ == "__main__":
    ClientApp().run()

