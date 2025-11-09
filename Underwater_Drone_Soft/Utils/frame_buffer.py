import threading

class FrameBuffer:
    def __init__(self):
        self.frame = None
        self.lock = threading.Lock()