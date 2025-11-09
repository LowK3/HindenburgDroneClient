import cv2, numpy as np, threading, time

class DisplayThread:
    def __init__(self, fb):
        self.fb = fb
        self.stop = threading.Event()

    def run(self):
        win = "Submarine Feed"
        cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)
        while not self.stop.is_set():
            with self.fb.lock:
                frame = None if self.fb.frame is None else self.fb.frame.copy()
            if frame is not None:
                cv2.imshow(win, frame)
            else:
                blank = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(blank, "Waiting for stream...", (60, 240),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255),2)
                cv2.imshow(win, blank)
            if cv2.waitKey(1) == 27:
                self.stop.set()
            time.sleep(0.01)
        cv2.destroyAllWindows()