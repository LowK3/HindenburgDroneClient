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