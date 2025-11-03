import socket
import struct
import cv2
import numpy as np
import threading
import time
import sys

UDP_PORT = 37020          # UDP discovery port
SERVER_PORT = 8485         # TCP video port (server's listening port)
BUFFER_SIZE = 65536
UDP_TIMEOUT = 3.0
TCP_TIMEOUT = 5.0
CON_INTERVAL = 2.0
DATA_WAIT = 10.0

class FrameBuffer:
    def __init__(self):
        self.frame = None
        self.lock = threading.Lock()

def discover_server(udp_sock, timeout=UDP_TIMEOUT):
    #Broadcast 'PC_CLIENT' and wait for server reply 'PI_CAM:PORT'.
    udp_sock.settimeout(timeout)
    try:
        udp_sock.sendto(b"PC_CLIENT", ('255.255.255.255', UDP_PORT))
    except Exception as e:
        print(f"Broadcast failed: {e}")
        return None, None

    start = time.time()
    while time.time() - start < timeout:
        try:
            data, addr = udp_sock.recvfrom(1024)
            if not data:
                continue
            try:
                msg = data.decode()
            except:
                continue
            if msg.startswith("PI_SERVER:"):
                try:
                    port = int(msg.split(":")[1])
                except:
                    port = SERVER_PORT
                return addr[0], port
        except socket.timeout:
            break
        except Exception:
            break
    return None, None

def recv_all(sock, length):
    #Receive exactly length bytes or raise.
    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            raise ConnectionResetError("Socket closed while reading")
        data += chunk
    return data

def network_thread(frame_buffer, shutdown_event):
    #Discovery via UDP, then TCP receive loop for frames.
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    tcp_sock = None
    last_data = 0
    connected = False

    try:
        while not shutdown_event.is_set():
            if not connected:
                print("Searching for server via UDP broadcast...")
                server_ip, server_port = discover_server(udp_sock)
                if not server_ip:
                    time.sleep(CON_INTERVAL)
                    continue

                print(f"Discovered server at {server_ip}:{server_port}. Connecting TCP...")
                try:
                    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tcp_sock.settimeout(TCP_TIMEOUT)
                    tcp_sock.connect((server_ip, server_port))
                    tcp_sock.settimeout(None)
                    connected = True
                    last_data = time.time()
                    print("TCP connection established.")
                except Exception as e:
                    print("TCP connection error:", e)
                    if tcp_sock:
                        tcp_sock.close()
                        tcp_sock = None
                    connected = False
                    time.sleep(CON_INTERVAL)
                    continue

            # Receive length-prefixed frames: 4-byte unsigned little-endian length
            try:
                header = recv_all(tcp_sock, 4)
                frame_len = struct.unpack("<I", header)[0]
                if frame_len == 0 or frame_len > 10_000_000:
                    print(f"Invalid frame length: {frame_len}")
                    raise ConnectionResetError("Invalid frame length")
                image_data = recv_all(tcp_sock, frame_len)
                last_data = time.time()

                np_img = np.frombuffer(image_data, dtype=np.uint8)
                frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
                if frame is not None:
                    with frame_buffer.lock:
                        frame_buffer.frame = frame
                else:
                    print("Warning: failed to decode JPEG frame")

            except Exception as e:
                print("Stream/read error:", e)
                # Close TCP and go back to discovery
                try:
                    if tcp_sock:
                        tcp_sock.close()
                except:
                    pass
                tcp_sock = None
                connected = False
                with frame_buffer.lock:
                    frame_buffer.frame = None
                time.sleep(0.5)
                continue

            # if no data for a while, reconnect
            if time.time() - last_data > DATA_WAIT:
                print("No frames received for a while. Reconnecting...")
                try:
                    if tcp_sock:
                        tcp_sock.close()
                except:
                    pass
                tcp_sock = None
                connected = False
                with frame_buffer.lock:
                    frame_buffer.frame = None

    finally:
        try:
            udp_sock.close()
        except:
            pass
        if tcp_sock:
            try:
                tcp_sock.close()
            except:
                pass

def display_thread(frame_buffer, shutdown_event):
    print("Starting display...")
    window_name = "Drone Server"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    while not shutdown_event.is_set():
        frame = None
        with frame_buffer.lock:
            if frame_buffer.frame is not None:
                frame = frame_buffer.frame.copy()

        if frame is not None:
            cv2.imshow(window_name, frame)
        else:
            blank = np.zeros((1920, 1080, 3), dtype=np.uint8)
            cv2.putText(blank, "Waiting for stream...", (80, 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.imshow(window_name, blank)

        key = cv2.waitKey(1) & 0xFF
        # exit on ESC or window close
        if key == 27 or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

        time.sleep(0.01)

    cv2.destroyAllWindows()
    shutdown_event.set()

def main():
    fb = FrameBuffer()
    shutdown_event = threading.Event()

    try:
        net_thread = threading.Thread(target=network_thread, args=(fb, shutdown_event), daemon=True)
        net_thread.start()

        display_thread(fb, shutdown_event)

    except KeyboardInterrupt:
        print("\nCtrl+C received. Client shutting down...")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        shutdown_event.set()
        print("Client shutting down...")
        net_thread.join(2.0)
        sys.exit(0)

if __name__ == "__main__":
    main()