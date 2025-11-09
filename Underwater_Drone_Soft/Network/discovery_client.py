import socket, time
from config import UDP_PORT

class DiscoveryClient:
    def __init__(self, timeout=3.0):
        self.timeout = timeout

    def discover(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(self.timeout)
        try:
            sock.sendto(b"PC_CLIENT", ('255.255.255.255', UDP_PORT))
            start = time.time()
            while time.time() - start < self.timeout:
                data, addr = sock.recvfrom(1024)
                msg = data.decode(errors="ignore")
                if msg.startswith("PI_SERVER:"):
                    return addr[0], int(msg.split(":")[1])
        except Exception:
            return None, None
        finally:
            sock.close()
        return None, None