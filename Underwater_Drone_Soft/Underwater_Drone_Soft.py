import socket
import struct
import cv2
import numpy as np
import time

SERVER_PORT = 8485
BUFFER_SIZE = 65535
TIMEOUT = 3.0
RECONNECT_INTERVAL = 2.0

def setup_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(TIMEOUT)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    return s

def discover_pi(s):
    print("Searching for server...")
    while True:
        try:
            s.sendto(b"PC_CLIENT", ('255.255.255.255', SERVER_PORT))
            packet, addr = s.recvfrom(BUFFER_SIZE)
            print(f"Server connected: {addr}")
            return addr
        except socket.timeout:
            print("No response. Retrying...")
            time.sleep(RECONNECT_INTERVAL)

def main():
    s = setup_socket()
    server_addr = None
    packets = {}
    frame_id = None

    while True:
        if not server_addr:
            server_addr = discover_pi(s)
            packets.clear()
            frame_id = None

        try:
            packet, addr = s.recvfrom(BUFFER_SIZE)
            fid, chunk_id, total_size = struct.unpack("<III", packet[:12])
            chunk = packet[12:]

            if fid != frame_id:
                frame_id = fid
                packets = {}

            packets[chunk_id] = chunk
            assembled = b"".join(packets[i] for i in sorted(packets.keys()))
            if len(assembled) >= total_size:
                np_img = np.frombuffer(assembled, dtype=np.uint8)
                frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
                if frame is not None:
                    cv2.imshow("Drone stram", frame)
                if cv2.waitKey(1) == 27:
                    break

        except socket.timeout:
            print("Connection timeout. Trying to reconnect...")
            server_addr = None

        except OSError as e:
            print(f"Socket error: {e}")
            server_addr = None
            time.sleep(1)

        except Exception as e:
            print("Unexpected error:", e)
            time.sleep(1)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()