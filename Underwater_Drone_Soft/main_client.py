import threading
from camera_client import start_video_display
from control_client import SubmarineClient

SERVER_IP = "192.168.2.10"  # your Pi’s static IP

def main():
    control = SubmarineClient(SERVER_IP, port=9000)
    t_ctrl = threading.Thread(target=lambda: control.run(), daemon=True)

    t_ctrl.start()
    start_video_display(SERVER_IP, video_port=8485)

    print("[MainClient] Camera display closed. Stopping control thread.")
    control.input_handler.running = False
    t_ctrl.join()

if __name__ == "__main__":
    main()
