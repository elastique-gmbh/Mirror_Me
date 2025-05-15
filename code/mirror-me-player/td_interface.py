import time
import socket
import json
from mirrorbot import MirrorBot
import socket

class TouchDesignerInterface:

    def __init__(self, botA:MirrorBot, botB:MirrorBot, window, loadRef, homeRef, startRef) -> None:
        self.bots = [botA, botB]
        self.loadRef = loadRef
        self.homeRef = homeRef
        self.startRef = startRef
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", 7001))
        pass

    def inputLoop(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            if addr[0] == "127.0.0.1":
                message = data.decode("utf-8").strip()
                if message.startswith("start: "):
                    print(message)
                    parts = message.split(": ")
                    id = int(parts[1][0:1])
                    self.loadRef(id)
                if message.startswith("home"):
                    self.homeRef()
                if message.startswith("start_program"):
                    self.startRef()

    def outputLoop(self):
        while True:
            time.sleep(0.5)
            status = []
            for bot in self.bots:
                status.append(bot.getStatus())
            data = (json.dumps(status)+"\n").encode()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(data, ("127.0.0.1", 7000))