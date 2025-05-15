import time, glob
from subprocess import PIPE, run
import os
import requests
import base64
import time
import shutil

class VideoUploader:
    def __init__(self, mapping, folder = "../touchdesigner/recordings/"):
        self.folder = folder
        self.audiomapping = mapping
        print("create uploader for folder:", folder)

    def loop(self):
        while True:
            try:
                self.uploadFiles()
            except Exception as e:
                print("error when uploading")
            time.sleep(1.0)

    def uploadFiles(self):
        start = glob.glob(self.folder+"start_upload*", recursive=False)
        if len(start) < 1:
            return
        os.unlink(self.folder+"start_upload.txt")
        print("upload triggered")
        files = glob.glob(self.folder+"*.mp4", recursive=False)
        for file in files:
            #print("start upload", file)
            self.processFile(file)

    def processFile(self, fileN):
        newFile = self.convertAudio(fileN)
        if newFile is None:
            return
        
        uuid = newFile[-43:-7]
        start = time.time()
        with open(newFile, "rb") as file:
            print("start upload: ", file)
            url = 'https://mirror-me.elastique.de/upload.php?uuid='+uuid
            bData = base64.b64encode(file.read())
            x = requests.post(url, bData)
            end = time.time()
            duration = end-start
            print("Upload complete, took: ", str(duration))

    def convertAudio(self, file):
        newfile = file.replace(".mp4", "_ac.mp4")
        if os.path.isfile(newfile) or file.endswith("_ac.mp4"):
            return
        file_stats = os.stat(file)
        if file_stats.st_size < 10000:
            return
        
        cmd = "ffmpeg/bin/ffmpeg.exe -y -i "+file+" -vcodec copy -codec:a aac "+newfile
        CREATE_NO_WINDOW = 0x08000000
        result = run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True, creationflags=CREATE_NO_WINDOW)
        #print(result.returncode, result.stdout, result.stderr)
        return newfile