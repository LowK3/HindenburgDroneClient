import sys
import threading
from PySide6.QtWidgets import QApplication
from Video.gui import VideoWindow
from Utils.frame_buffer import FrameBuffer
from Network.network_worker import NetworkWorker
from Utils.common import log

class ClientApp:
    def __init__(self):
        self.fb = FrameBuffer()
        self.stop_event = threading.Event()

    def run(self):
        # Start networking thread
        net = NetworkWorker(self.fb, self.stop_event)
        net_thread = threading.Thread(target=net.run, daemon=True)
        net_thread.start()

        # Start Qt GUI (Main Thread)
        app = QApplication(sys.argv)
        window = VideoWindow(self.fb, net.control)

        exit_code = app.exec()

        # Shutdown
        log("GUI closed, stopping network.")
        self.stop_event.set()
        net_thread.join(timeout=2.0)

        sys.exit(exit_code)

if __name__ == "__main__":
    ClientApp().run()

