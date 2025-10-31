import cv2
import socket
import struct
import numpy as np

TCP_PORT = None
UDP_PORT = 37020
PI_IP = None

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", UDP_PORT))
s.settimeout(5)

print("Listening for Pi Server broadcast...")
while True:
    try:
        data, addr = s.recvfrom(1024)
        msg = data.decode().strip()
        if msg.startswith("PI_Server:"):
            TCP_PORT = int(msg.split(":")[1])
            PI_IP = addr[0]
            print(f"Discovered Raspberry Server: {PI_IP}:{TCP_PORT}")
            break
    except socket.timeout:
        print("No broadcast yet. Retrying...")
s.close()

if not PI_IP:
    print("Could not find Pi Server.")
    exit()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Connecting to Raspberry camera...")
client_socket.connect((PI_IP, TCP_PORT))
connection = client_socket.makefile('rb')
print("Connected!")

payload_size = struct.calcsize("<L")

try:
    while True:
        image_len_data = connection.read(payload_size)
        if not image_len_data:
            break
        
        image_len = struct.unpack(">L", image_len_data)[0]
        if image_len == 0:
            continue
        
        image_data = b""
        
        while len(image_data) < image_len:
            image_data += connection.read(image_len - len(image_data))
        
        np_image = np.frombuffer(image_data, dtype=np.uint8)
        frame = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        if frame is None:
            print("Warning: failed to decode frame")
            continue

        cv2.imshow("Raspberry Pi Camera Stream", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break
finally:
    cv2.destroyAllWindows()
    connection.close()
    client_socket.close()

