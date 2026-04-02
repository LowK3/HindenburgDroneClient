import socket
import time
import traceback
from config import (
    UDP_DISCOVERY_PORT, UDP_TIMEOUT, CON_INTERVAL, HANDSHAKE_EXPECTED, HANDSHAKE_REPLY_PREFIX,
    DISCOVERY_RECV_CHUNK
)
from Utils.logger import log

class DiscoveryClient:
    """Handles UDP broadcast discovery of the server."""
    def __init__(self):
        self.sock = None

    def discover(self):
        """Broadcast PC_CLIENT and wait for PI_SERVER:<port> response."""
        try:
            if self.sock is None:
                self.sock = self._create_socket()

            self.sock.sendto(HANDSHAKE_EXPECTED, ("<broadcast>", UDP_DISCOVERY_PORT))

            start = time.time()
            while time.time() - start < UDP_TIMEOUT:
                try:
                    data, addr = self.sock.recvfrom(DISCOVERY_RECV_CHUNK)
                except socket.timeout:
                    break
                if not data:
                    continue
                msg = data.decode(errors="ignore")
                if msg.startswith(f"{HANDSHAKE_REPLY_PREFIX}:"):
                    try:
                        port = int(msg.split(":")[1])
                    except (IndexError, ValueError):
                        continue
                    log(f"Discovered server at {addr[0]}:{port}")
                    return addr[0], port
            print("No discovery reply received")
        except Exception as e:
            log(f"Discovery error: {e}\n{traceback.format_exc()}")
            # finally:
            self.stop()
        return None, None

    def _create_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(("0.0.0.0", 0))
        s.settimeout(UDP_TIMEOUT)
        return s

    def stop(self):
        if self.sock:
            try:
                self.sock.close()
                print("UDP discovery socket closed.")
            except Exception as e:
                log(f"Error closing UDP socket: {e}\n{traceback.format_exc()}")
            self.sock = None
