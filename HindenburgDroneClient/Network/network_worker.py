import time
import threading
from Network.discovery_client import DiscoveryClient
from Network.udp_video_client import VideoClient
from Network.tcp_control_client import ControlClient
from config import RECONNECT_DELAY
from Utils.logger import log

class NetworkWorker:
    def __init__(self, frame_buffer, stop_event):
        self.fb = frame_buffer
        self._stop_event = stop_event
        self.discovery = DiscoveryClient()
        self.video = VideoClient()
        self.control = ControlClient()

    def run(self):
        log("Network worker started. Searching for drone...")
        while not self._stop_event.is_set():
            if self._establish_connection():
                self._stream_loop()
            self._stop_connection()
            
            if not self._stop_event.is_set():
                print("Disconnected. Returning to discovery...")
            time.sleep(RECONNECT_DELAY)
        log("Network shut down.")

    def _establish_connection(self):
        ip, port = self.discovery.discover()
        if not ip or self._stop_event.is_set():
            time.sleep(RECONNECT_DELAY)
            return False

        if not self.video.connect(ip, port):
            time.sleep(RECONNECT_DELAY)
            return False

        if not self.control.connect(ip):
            self.video.stop()
            time.sleep(RECONNECT_DELAY)
            return False

        log(f"Fully connected to Drone at {ip}.")
        return True

    def _stream_loop(self):
        while not self._stop_event.is_set() and self.control.is_connected():
            try:
                frame = self.video.receive_frame()
                if frame is not None:
                    with self.fb.lock:
                        self.fb.frame = frame
                        self.fb.new_frame = True
            except TimeoutError:
                with self.fb.lock:
                    self.fb.frame = None
                    self.fb.new_frame = True
                continue
            except ConnectionResetError as e:
                log(f"Video connection reset: {e}")
                break
            except Exception as e:
                log(f"Network error: {e}")
                time.sleep(0.1)
                break

    def _stop_connection(self):
        self.video.stop()
        self.control.stop()
        with self.fb.lock:
            self.fb.frame = None
