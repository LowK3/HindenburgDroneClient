import socket
import struct
import time
import simplejpeg
from config import (
    UDP_VIDEO_PORT, VIDEO_STREAM_TIMEOUT, UDP_BUFFER_SIZE, VIDEO_HEADER_SIZE, MAGIC_BYTE, 
    FRAME_BUFFER_LIMIT, UDP_VIDEO_TIMEOUT
)
from Utils.logger import log

class VideoClient:
    def __init__(self):
        self.sock = None
        self.last_data_time = 0
        self.frame_buffer = {}

    def connect(self, ip: str, port: int):
        self.stop()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", UDP_VIDEO_PORT))
        self.sock.settimeout(UDP_VIDEO_TIMEOUT)
        self.last_data_time = time.time()
        log(f"UDP Video client bound to port {UDP_VIDEO_PORT}.")
        return True

    def receive_frame(self):
        if not self.sock:
            raise ConnectionError("Socket not bound.")

        while True:
            try:
                packet, addr = self.sock.recvfrom(UDP_BUFFER_SIZE)
                self.last_data_time = time.time()

                if len(packet) < VIDEO_HEADER_SIZE: continue

                magic, frame_id, chunk_idx, total_chunks = struct.unpack("<BIBB", packet[:VIDEO_HEADER_SIZE])
                if magic != MAGIC_BYTE: continue

                if frame_id not in self.frame_buffer:
                    self.frame_buffer[frame_id] = {}

                self.frame_buffer[frame_id][chunk_idx] = packet[VIDEO_HEADER_SIZE:]

                # If we have received all chunks for this frame
                if len(self.frame_buffer[frame_id]) == total_chunks:
                    data = b"".join([self.frame_buffer[frame_id][i] for i in range(total_chunks)])
                    
                    # Clean up old frames to prevent memory leaks
                    keys_to_delete = [k for k in self.frame_buffer.keys() if k <= frame_id]
                    for k in keys_to_delete: del self.frame_buffer[k]

                    if len(self.frame_buffer) > FRAME_BUFFER_LIMIT:
                        self.frame_buffer.clear()

                    try:
                        return simplejpeg.decode_jpeg(data, colorspace='BGR')
                    except Exception:
                        return None
            except socket.timeout:
                if time.time() - self.last_data_time > VIDEO_STREAM_TIMEOUT:
                    raise TimeoutError("No video data from server.")
                return None
            except Exception as e:
                raise ConnectionResetError(f"UDP receive error: {e}\n")

    def stop(self):
        if self.sock:
            self.sock.close()
            log("UDP video socket closed.")
        self.sock = None
