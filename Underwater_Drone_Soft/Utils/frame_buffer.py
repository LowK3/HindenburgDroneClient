import threading

class FrameBuffer:
    def __init__(self):
        import threading
        self.lock = threading.Lock()
        self.frame = None