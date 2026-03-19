import socket, time, traceback
from config import UDP_PORT, UDP_TIMEOUT, CON_INTERVAL
from Utils.logger import log

class DiscoveryClient:
    """Handles UDP broadcast discovery of the server."""
    def __init__(self):
        self.sock = None

    def create_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(("0.0.0.0", 0))
        s.settimeout(UDP_TIMEOUT)
        return s

    def discover(self):
        """Broadcast PC_CLIENT and wait for PI_SERVER:<port> response."""
        try:
            if self.sock is None:
                self.sock = self.create_socket()

            self.sock.sendto(b"PC_CLIENT", ("<broadcast>", UDP_PORT))

            start = time.time()
            while time.time() - start < UDP_TIMEOUT:
                try:
                    data, addr = self.sock.recvfrom(1024)
                except socket.timeout:
                    break
                if not data:
                    continue
                msg = data.decode(errors="ignore")
                if msg.startswith("PI_SERVER:"):
                    try:
                        port = int(msg.split(":")[1])
                    except:
                        continue
                    log(f"Discovered server at {addr[0]}:{port}")
                    return addr[0], port
            print("No discovery reply received")
        except Exception as e:
            log(f"Discovery error: {e}\n{traceback.format_exc()}")
        finally:
            self.stop()
        return None, None

    def stop(self):
        if self.sock:
            try:
                self.sock.close()
                print("UDP discovery socket closed.")
            except Exception as e:
                log(f"Error closing UDP socket: {e}\n{traceback.format_exc()}")
            self.sock = None
