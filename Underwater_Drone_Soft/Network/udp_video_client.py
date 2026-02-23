import socket, struct, cv2, numpy as np, time, simplejpeg, traceback
from config import UDP_VIDEO_PORT, DATA_WAIT
from Utils.common import log

class VideoClient:
    def __init__(self):
        self.sock = None
        self.last_data_time = 0
        self.frame_buffer = {}

    def connect(self, ip, port):
        self.stop()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", UDP_VIDEO_PORT))
        self.sock.settimeout(1.0)
        self.last_data_time = time.time()
        log(f"UDP Video client bound to port {UDP_VIDEO_PORT}.")
        return True

    def receive_frame(self):
        if not self.sock:
            raise ConnectionError("Socket not bound.")

        while True:
            try:
                packet, addr = self.sock.recvfrom(65536)  # Buffer size large enough for UDP packet
                self.last_data_time = time.time()

                if len(packet) < 7: continue

                magic, frame_id, chunk_idx, total_chunks = struct.unpack("<BIBB", packet[:7])
                if magic != 0xAA: continue

                if frame_id not in self.frame_buffer:
                    self.frame_buffer[frame_id] = {}

                self.frame_buffer[frame_id][chunk_idx] = packet[7:]

                # If we have received all chunks for this frame
                if len(self.frame_buffer[frame_id]) == total_chunks:
                    data = b"".join([self.frame_buffer[frame_id][i] for i in range(total_chunks)])
                    
                    # Clean up old frames to prevent memory leaks
                    keys_to_delete = [k for k in self.frame_buffer.keys() if k <= frame_id]
                    for k in keys_to_delete: del self.frame_buffer[k]

                    if len(self.frame_buffer) > 100:
                        self.frame_buffer.clear()

                    try:
                        return simplejpeg.decode_jpeg(data, colorspace='RGB')
                    except:
                        return None

            except socket.timeout:
                if time.time() - self.last_data_time > DATA_WAIT:
                    raise TimeoutError("No video data from server.")
                return None
            except Exception as e:
                raise ConnectionResetError(f"UDP receive error: {e}\n{traceback.format_exc()}")

    def stop(self):
        if self.sock:
            self.sock.close()
            log("UDP video socket closed.")
        self.sock = None
