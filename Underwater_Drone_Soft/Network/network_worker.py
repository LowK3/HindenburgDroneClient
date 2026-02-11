import time
from Network.discovery_client import DiscoveryClient
from Network.tcp_video_client import VideoClient
from Network.tcp_control_client import ControlClient
from Utils.common import log
from config import CON_INTERVAL

class NetworkWorker:
    def __init__(self, frame_buffer, stop_event):
        self.fb = frame_buffer
        self.stop_event = stop_event
        self.discovery = DiscoveryClient()
        self.video = VideoClient()
        self.control = ControlClient()

    def run(self):
        log("Network started")

        while not self.stop_event.is_set():
            # Discovery server
            ip, port = self.discovery.discover()
            if not ip or self.stop_event.is_set():
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

            # Streaming loop
            while not self.stop_event.is_set():
                try:
                    frame = self.video.receive_frame()
                    if frame is not None:
                        with self.fb.lock:
                            self.fb.frame = frame

                except Exception as e:
                    log(f"Network error: {e}")
                    break

            # Cleanup and back to discovery
            self.video.stop()
            with self.fb.lock:
                self.fb.frame = None

            log("Disconnected. Returning to discovery...")
            time.sleep(CON_INTERVAL)

        log("Network shutting down")
