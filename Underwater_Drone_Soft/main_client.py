"""

import threading, time, sys

from Network.discovery_client import DiscoveryClient
from Network.tcp_video_client import TCPClient
from Network.tcp_control_client import ControlClient

from Video.display import DisplayThread
from Utils.frame_buffer import FrameBuffer

from Control.keyboard_input import KeyboardInput

from Utils.common import log
from config import CON_INTERVAL

from PySide6.QtWidgets import QApplication
from Video.gui import VideoWindow
import sys


class ClientApp:
    def __init__(self):
        self.shutdown = threading.Event()

        self.fb = FrameBuffer()
        #self.display = DisplayThread(self.fb)

        self.discovery = DiscoveryClient()
        self.video = TCPClient()
        self.control = ControlClient()

        self.keyboard = None
        self.keyboard_thread = None

    def run(self):
        # Launch display 
        display_thread = threading.Thread(target=self.display.run, daemon=True)
        display_thread.start()

        log("Client started. Press ESC to exit.")

        while not self.display.stop.is_set():
            # Discovery server
            ip, port = self.discovery.discover()
            if not ip:
                time.sleep(CON_INTERVAL)
                continue

            # Connect video TCP
            if not self.video.connect(ip, port):
                time.sleep(CON_INTERVAL)
                continue

            # Connect control TCP
            if not self.control.connect(ip):
                self.video.stop()
                time.sleep(CON_INTERVAL)
                continue

            # Start keyboard controller
            self.keyboard = KeyboardInput(self.control)
            self.keyboard_thread = threading.Thread(
                target=self.keyboard.run,
                daemon=True
            )
            self.keyboard_thread.start()

            # Streaming loop
            while not self.display.stop.is_set():
                try:
                    frame = self.video.receive_frame()
                    if frame is not None:
                        with self.fb.lock:
                            self.fb.frame = frame
                except (TimeoutError, ConnectionResetError, OSError) as e:
                    log(f"Connection lost or timed out: {e}")
                    break
                except Exception as e:
                    log(f"Stream error: {e}")
                    break

            # cleanup and back to discovery
            self.cleanup_after_disconnect()
            log("Reconnecting to server...")
            time.sleep(1.0)

        log("Display closed, shutting down client.")
        self.stop()

    def cleanup_after_disconnect(self):
        if self.keyboard:
            self.keyboard.stop.set()
        if self.control:
            self.control.stop()
        if self.video:
            self.video.stop()
        with self.fb.lock:
            self.fb.frame = None

    def stop(self):
        self.cleanup_after_disconnect()
        self.display.stop.set()
        self.discovery.stop()

if __name__ == "__main__":
    try:
        ClientApp().run()
    except KeyboardInterrupt:
        log("KeyboardInterrupt, exiting...")
        sys.exit(0)

 """

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

        # Start Qt GUI (MAIN THREAD)
        app = QApplication(sys.argv)
        window = VideoWindow(self.fb)

        exit_code = app.exec()

        # Shutdown
        log("GUI closed, stopping network")
        self.stop_event.set()
        net_thread.join(timeout=2.0)

        sys.exit(exit_code)

if __name__ == "__main__":
    ClientApp().run()

