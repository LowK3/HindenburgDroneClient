import cv2, numpy as np

def get_screen_size():
    """Try several methods to get the real screen resolution (tkinter, Windows API), fallback to 1920x1080."""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        root.destroy()
        return w, h
    except Exception:
        pass

    try:
        from ctypes import windll
        user32 = windll.user32
        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    except Exception:
        pass

    return 1920, 1080

def letterbox(img, target_w, target_h, color=(0, 0, 0)):
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