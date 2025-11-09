import cv2, numpy as np, threading, time
from Utils.get_screen_size import get_screen_size

class DisplayThread:
    def __init__(self, fb):
        self.fb = fb
        self.stop = threading.Event()

    def _letterbox(self, img, target_w, target_h, color=(0, 0, 0)):
        """Scale img to fit inside target while preserving aspect ratio and center it on a background."""
        h, w = img.shape[:2]
        scale = min(target_w / w, target_h / h)
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        top = (target_h - new_h) // 2
        left = (target_w - new_w) // 2
        out = np.full((target_h, target_w, 3), color, dtype=np.uint8)
        out[top:top + new_h, left:left + new_w] = resized
        return out

    def run(self):
        win = "Submarine Stream"
        screen_w, screen_h = get_screen_size()

        # Windowed-fullscreen: a normal, resizable window resized to cover the screen
        cv2.namedWindow(win, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(win, screen_w, screen_h)
        cv2.moveWindow(win, 0, 0)

        while not self.stop.is_set():
            with self.fb.lock:
                frame = None if self.fb.frame is None else self.fb.frame.copy()

            if frame is not None:
                # Ensure 3 channels
                if frame.ndim == 2:
                    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

                # Preserve aspect ratio and fit to screen (letterbox)
                fh, fw = frame.shape[:2]
                if (fw, fh) != (screen_w, screen_h):
                    frame = self._letterbox(frame, screen_w, screen_h)
                cv2.imshow(win, frame)
            else:
                # Blank 3-channel frame sized to current screen
                blank = np.zeros((screen_h, screen_w, 3), dtype=np.uint8)
                text = "Waiting for stream..."
                font = cv2.FONT_HERSHEY_SIMPLEX
                # Scale font/thickness with screen width so it looks reasonable on different resolutions
                font_scale = max(0.6, min(2.5, screen_w / 1280.0))
                thickness = max(1, int(round(screen_w / 800.0)))
                (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)
                x = (screen_w - tw) // 2
                y = (screen_h + th) // 2
                cv2.putText(blank, text, (x, y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
                cv2.imshow(win, blank)

            if cv2.waitKey(1) == 27:
                self.stop.set()
            time.sleep(0.01)

        cv2.destroyAllWindows()