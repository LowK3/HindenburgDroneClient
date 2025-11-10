import threading, time, sys
from Network.discovery_client import DiscoveryClient
from Network.tcp_video_client import TCPClient
from Video.display import DisplayThread
from Utils.common import log
from Utils.frame_buffer import FrameBuffer
from config import CON_INTERVAL

class ClientApp:
    def __init__(self):
        self.shutdown = threading.Event()
        self.fb = FrameBuffer()
        self.display = DisplayThread(self.fb)
        self.discovery = DiscoveryClient()
        self.tcp = TCPClient()

    def run(self):
        # Launch display
        display_thread = threading.Thread(target=self.display.run, daemon=True)
        display_thread.start()

        log("Client started. Press ESC in the window to exit.")

        while not self.display.stop.is_set():
            # Discovery loop
            ip, port = self.discovery.discover()
            if not ip:
                time.sleep(CON_INTERVAL)
                continue

            # Try connecting
            if not self.tcp.connect(ip, port):
                time.sleep(CON_INTERVAL)
                continue

            # Streaming loop
            while not self.display.stop.is_set():
                try:
                    frame = self.tcp.receive_frame()
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
            self.tcp.stop()
            with self.fb.lock:
                self.fb.frame = None
            log("Reconnecting to server...")
            time.sleep(1.0)

        log("Display closed, shutting down client.")
        self.stop()

    def stop(self):
        self.discovery.stop()
        self.tcp.stop()
        self.display.stop.set()

if __name__ == "__main__":
    try:
        app = ClientApp()
        app.run()
    except KeyboardInterrupt:
        log("KeyboardInterrupt, exiting...")
        sys.exit(0)
