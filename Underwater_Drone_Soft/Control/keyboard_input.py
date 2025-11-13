import threading, time, keyboard # pip install keyboard

from Utils.common import log

class KeyboardInput:
    def __init__(self, control_client):
        self.client = control_client
        self.stop = threading.Event()

    def run(self):
        while not self.stop.is_set():
            if keyboard.is_pressed("w"): self.client.send("W")
            elif keyboard.is_pressed("s"): self.client.send("S")
            elif keyboard.is_pressed("a"): self.client.send("A")
            elif keyboard.is_pressed("d"): self.client.send("D")

            elif keyboard.is_pressed("u"): self.client.send("UP")
            elif keyboard.is_pressed("j"): self.client.send("DOWN")

            elif keyboard.is_pressed("o"): self.client.send("REAR+")
            elif keyboard.is_pressed("l"): self.client.send("REAR-")

            elif keyboard.is_pressed("i"): self.client.send("FRONT+")
            elif keyboard.is_pressed("k"): self.client.send("FRONT-")

            else:
                self.client.send("STOP")

            time.sleep(0.05)
