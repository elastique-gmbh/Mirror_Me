import rtdeState
import csv
import time
import math
import socket
from enum import Enum

class RuntimeStatus(Enum):
    Stopping = 0
    Stopped = 1
    Running = 2
    Pausing = 3
    Paused = 4
    Resuming = 5
    Offline = -1


class MirrorBot:

    def __init__(self, id, ip, port = 30004) -> None:
        self.id = id
        self.ROBOT_HOST = ip
        self.ROBOT_PORT = port
        self.config_filename = 'rtdeCommand.xml'
        self.ip = ip
        self.q1 = []
        self.q2 = []
        self.q3 = []
        self.q4 = []
        self.q5 = []
        self.q6 = []
        self.filename = ""
        self.cmd = ""
        self.currentState = None
        self.isHomed = False
        self.currentSpeed = 30
        self.playStatus = False
        self.totalFrames = 100
        self.currentFrame = 0

    def loop(self, window):
        self.window = window
        self.rtde = rtdeState.RtdeState(self.ROBOT_HOST, self.config_filename, frequency=240)
        self.rtde.initialize()

        while True:
            if self.cmd == "start":
                self.startCurrent()
            if self.cmd == "home":
                self.moveHome()
            self.cmd = ""
            self.isHomed = self.checkDistance(0)
            time.sleep(0.01)
    
    def startCurrent(self):
        if len(self.q1) < 1:
            print("no file loaded / no valid points")
            return
        
        if not self.checkDistance(0):
            print("Joint positions are too far from start, please home the Bot first")
            return
        self.playStatus = True
        self.rtde.set_q.input_double_register_0 = self.q1[0]
        self.rtde.set_q.input_double_register_1 = self.q2[0]
        self.rtde.set_q.input_double_register_2 = self.q3[0]
        self.rtde.set_q.input_double_register_3 = self.q4[0]
        self.rtde.set_q.input_double_register_4 = self.q5[0]
        self.rtde.set_q.input_double_register_5 = self.q6[0]
        self.rtde.servo.input_int_register_0 = 0
        print("Playing back", len(self.q1), "Points with", self.currentSpeed, "FPS")
        self.rtde.servo.input_int_register_0 = 2
        self.rtde.con.send(self.rtde.servo)
        time.sleep(0.01)
        startTime = time.time()
        #lastFrame = time.time()
        #print("start at: ", startTime)
        # Main control loop. Receive an output packet from the robot and then send the next joint positions.
        for i in range(len(self.q1)):
            #self.rtde.receive()
            #framestart = time.time()
            now = time.time()
            #print(now-lastFrame)
            self.list_to_set_q(self.rtde.set_q, [self.q1[i], self.q2[i], self.q3[i], self.q4[i], self.q5[i], self.q6[i]])
            self.rtde.con.send(self.rtde.set_q)
            #lastFrame = time.time()
            startTime = startTime + 1/self.currentSpeed
            if not self.isRunning():
                self.window.write_event_value('-stop-during-run-', '')
                print("Bot Program NOT running, stopping Playback")
                self.playStatus = True
                break
            self.currentFrame = i
            self.totalFrames = len(self.q1)
            self.window.write_event_value('-progress_'+self.id+'-', [self.currentFrame, self.totalFrames])
            delay = startTime - time.time()
            if delay > 0:
                time.sleep(delay)

        endTime = time.time()
        print("Playback finished, took:", endTime-startTime, "seconds")
        self.currentFrame = 0
        self.playStatus = False
        self.rtde.servo.input_int_register_0 = 0
        self.rtde.con.send(self.rtde.servo)
    
    def checkDistance(self, i):
        self.receiveState()
        try:
            self.checkAngleDistance(self.q1[i], self.currentState.actual_q[0])
            self.checkAngleDistance(self.q2[i], self.currentState.actual_q[1])
            self.checkAngleDistance(self.q3[i], self.currentState.actual_q[2])
            self.checkAngleDistance(self.q4[i], self.currentState.actual_q[3])
            self.checkAngleDistance(self.q5[i], self.currentState.actual_q[4])
            self.checkAngleDistance(self.q6[i], self.currentState.actual_q[5])
        except Exception:
            return False
        return True

    def checkAngleDistance(self, angle, currentAngle):
        if abs(angle-currentAngle) > 0.05:
            raise Exception("Joint difference to big to play")
        return True

    def receiveState(self):
        self.currentState = self.rtde.receive()
        #if self.currentState.runtime_state != RuntimeStatus.Running.value:
        #    self.isHomed = False

    def isRunning(self):
        if self.cmd == "stop":
            self.cmd = ""
            return False
        self.receiveState()
        if self.currentState.runtime_state == RuntimeStatus.Running.value:
            return True
        return False
    
    def moveHome(self):
        if len(self.q1) < 1:
            print("no file loaded / no valid points")
            return
        
        if not self.isRunning():
            print("Bot Program NOT running cannot start")
            return
        
        self.list_to_set_q(self.rtde.set_q, [self.q1[0], self.q2[0], self.q3[0], self.q4[0], self.q5[0], self.q6[0]])
        self.rtde.con.send(self.rtde.set_q)
        time.sleep(0.1)
        self.rtde.servo.input_int_register_0 = 1
        self.rtde.con.send(self.rtde.servo)
        startTime = time.time()
        print("Start Homing")
        ready = False
        self.receiveState()

        # Main control loop. Receive an output packet from the robot and then send the next joint positions.
        while not ready:
            ready = self.currentState.output_bit_register_64
            self.list_to_set_q(self.rtde.set_q, [self.q1[0], self.q2[0], self.q3[0], self.q4[0], self.q5[0], self.q6[0]])
            self.rtde.con.send(self.rtde.set_q)
            time.sleep(0.1)
            if not self.isRunning():
                break

        endTime = time.time()
        print("Homing finished:", endTime-startTime, "seconds")
        self.rtde.servo.input_int_register_0 = 0
        self.rtde.con.send(self.rtde.servo)

    def playCurrent(self):
        #if not self.wasHomed:
        #    print("NOT HOMED / will not start")
        #    return
        self.cmd = "start"

    def startHome(self):
        self.cmd = "home"

    def setSpeed(self, speed):
        self.currentSpeed = speed

    def stopBot(self):
        self.cmd = "stop"

    def sendDash(self, cmds):
        if self.currentState is None:
            return
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip, 29999))
            data = s.recv(1024)
            print(f"Received Dash Response {data!r}")
            for cmd in cmds:
                #time.sleep(0.15)
                s.sendall((cmd+"\n").encode())
                data = s.recv(1024)
                print(f"Received Dash Response {data!r}")

    def startProgram(self):
        self.sendDash(["load mirror-me.urp", "play"])
    
    def readFile(self, filename):
        try:
            print("reading file:", filename)
            #self.wasHomed = False
            self.filename = filename
            with open(filename, 'rt') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                self.q1 = []
                self.q2 = []
                self.q3 = []
                self.q4 = []
                self.q5 = []
                self.q6 = []
                for row in reader:
                    self.q1.append(float(row[0]))
                    self.q2.append(float(row[1]))
                    self.q3.append(float(row[2]))
                    self.q4.append(float(row[3]))
                    self.q5.append(float(row[4]))
                    self.q6.append(float(row[5]))
            print("File contains", len(self.q1), "Points")
        except Exception:
            print("could not load File")

    def list_to_set_q(self, set_q, list):
        for i in range(0, len(list)):
            set_q.__dict__["input_double_register_%i" % i] = list[i]
        return set_q
    
    def getStatus(self):
        data = {
            "id": self.id,
            "state": RuntimeStatus.Offline.value,
            "playState": self.playStatus,
            "homed": False,
            "totalFrames": self.totalFrames,
            "currentFrame": self.currentFrame
        }
        if self.currentState is None:
            return data
        
        data["state"] = self.currentState.runtime_state
        data["homed"] = self.isHomed
        return data