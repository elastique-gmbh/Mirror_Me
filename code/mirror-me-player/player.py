import FreeSimpleGUI as sg
import time
import threading
from mirrorbot import MirrorBot
import platform
import os
import glob
import winsound
from uploader import VideoUploader

from td_interface import TouchDesignerInterface

sg.theme('DarkBlack')

ipA = "10.100.0.125"
ipB = "10.100.0.126"

twoBots = True


if False: # for Virtual Bot
    ipA = "192.168.56.101"
    twoBots = False

dirs = next(os.walk('moves'))[1]
btns = []

wavFile = None

filemapping = []
for dir in dirs:
    btns.append(sg.Button(dir, key='-load_'+dir))
    filemapping.append(dir)

layout = [ 
    [sg.Text('Load Scene')],
    btns,
    [sg.Slider(range=(1, 120), default_value=30, expand_x=True, enable_events=True, orientation='horizontal', key='speed')],
    [sg.Button('START PROG', key="start_program_all"), sg.Button('HOME BOTH', key="home_all"), sg.Button('START BOTH', key="start_all")],
    [sg.Button('STOP', key="stop")],
    [sg.Output(size=(80,20))] ]

window = sg.Window('elastique - Mirror Me Player', layout, finalize=True)

botA = MirrorBot('a', ipA)
botB = MirrorBot('b', ipB)


def loadFile(name):
    fileA = glob.glob("moves/"+name+"/*_A.txt") + glob.glob("moves/"+name+"/*_A.csv")
    error = False
    if(len(fileA) != 1):
        print("Dir "+name+" does not contains exactly one text file for bot A")
        error = True
    fileB = glob.glob("moves/"+name+"/*_B.txt") + glob.glob("moves/"+name+"/*_B.csv")
    if(len(fileB) != 1):
        print("Dir "+name+" does not contains exactly one text file for bot B")
        error = True
    audioFile = glob.glob("moves/"+name+"/*.wav")
    wavFile = None
    if(len(audioFile) != 1):
        print("Dir "+name+" does not contains exactly one wav file")
    else:
        wavFile = audioFile[0]
    if not error:
        botA.readFile(fileA[0])
        botB.readFile(fileB[0])

def startId(id):
    loadFile(filemapping[id])
    window.write_event_value('start_all', '')

def startHome():
    window.write_event_value('home_all', '')

def startProgram():
    window.write_event_value('start_program_all', '')

td_interface = TouchDesignerInterface(botA, botB, window, startId, startHome, startProgram)

def bota_thread(window):
    botA.loop(window)
threading.Thread(target=bota_thread, args=(window,), daemon=True).start()

if twoBots:
    def botb_thread(window):
        botB.loop(window)
    threading.Thread(target=botb_thread, args=(window,), daemon=True).start()

def td_status_thread():
    td_interface.inputLoop()
threading.Thread(target=td_status_thread, args=(), daemon=True).start()

def td_input_thread():
    td_interface.outputLoop()
threading.Thread(target=td_input_thread, args=(), daemon=True).start()

uploader = VideoUploader(filemapping)

def uploader_thread():
    uploader.loop()
threading.Thread(target=uploader_thread, args=(), daemon=True).start()

loadFile(filemapping[0])

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    if event == "read_file_a":
        botA.readFile(values["filename_a"])
    if event == "read_file_b":
        botB.readFile(values["filename_b"])
    if event == "start_a":
        botA.playCurrent()
    if event == "start_b":
        botB.playCurrent()
    if event == "start_all":
        botA.playCurrent()
        botB.playCurrent()
        if wavFile is not None:
            winsound.PlaySound(wavFile, winsound.SND_ASYNC)
    if event == "home_all":
        botA.startHome()
        botB.startHome()
    if event == "start_program_all":
        botA.startProgram()
        botB.startProgram()
    if event == "home_a":
        botA.startHome()
    if event == "home_b":
        botB.startHome()
    if event == "stop":
        botA.stopBot()
        botB.stopBot()
        winsound.PlaySound(None, winsound.SND_PURGE)
    if event == "speed":
        botA.setSpeed(values["speed"])
        botB.setSpeed(values["speed"])
    if event == "-stop-during-run-":
        botA.stopBot()
        botB.stopBot()
    if event.startswith("-load_"):
        name = event[6:]
        loadFile(name)

    #if event == "-progress_a-":
    #    window['pbar_a'].update(values["-progress_a-"][0]/values["-progress_a-"][1])
    #if event == "-progress_b-":
    #    window['pbar_b'].update(values["-progress_b-"][0]/values["-progress_b-"][1])

window.close()