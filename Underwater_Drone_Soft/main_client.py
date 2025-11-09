import threading, time, sys
from network.discovery_client import DiscoveryClient
from network.tcp_video_client import TCPClient
from video.display import DisplayThread
from utils.frame_buffer import FrameBuffer
from config import CON_INTERVAL

def main():
    fb = FrameBuffer()
    display = DisplayThread(fb)
    tcp = TCPClient()
    discovery = DiscoveryClient()

    display_thread = threading.Thread(target=display.run, daemon=True)
    display_thread.start()

    while not display.stop.is_set():
        ip, port = discovery.discover()
        if not ip:
            time.sleep(CON_INTERVAL)
            continue
        print(f"Discovered server {ip}:{port}")
        try:
            tcp.connect(ip, port)
            while not display.stop.is_set():
                frame = tcp.receive_frame()
                if frame is not None:
                    with fb.lock:
                        fb.frame = frame
        except Exception as e:
            print("Connection lost:", e)
            tcp.close()
            with fb.lock:
                fb.frame = None
            time.sleep(CON_INTERVAL)

    tcp.close()
    print("Client exited")

if __name__ == "__main__":
    main()
