import threading, time, keyboard # pip install keyboard
from Utils.common import log

class KeyboardInput:
    def __init__(self, control_client):
        self.client = control_client
        self.stop = threading.Event()

    def run(self):
        while not self.stop.is_set():
            if keyboard.is_pressed("w"): self.client.send("W\n")
            elif keyboard.is_pressed("s"): self.client.send("S\n")
            elif keyboard.is_pressed("a"): self.client.send("A\n")
            elif keyboard.is_pressed("d"): self.client.send("D\n")

            elif keyboard.is_pressed("u"): self.client.send("UP\n")
            elif keyboard.is_pressed("j"): self.client.send("DOWN\n")

            elif keyboard.is_pressed("o"): self.client.send("REAR+\n")
            elif keyboard.is_pressed("l"): self.client.send("REAR-\n")

            elif keyboard.is_pressed("i"): self.client.send("FRONT+\n")
            elif keyboard.is_pressed("k"): self.client.send("FRONT-\n")

            else:
                self.client.send("STOP\n")

            time.sleep(0.05)
