import queue
import sounddevice as sd
import vosk
import sys
import json
import subprocess
import datetime
import re
import tkinter as tk
import threading
import os

class VoiceCommandWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("Offline Voice Command Assistant")

        self.label = tk.Label(self.root, text="Microphone", font=('Arial', 16))
        self.label.pack(pady=10)

        self.micButton = tk.Button(self.root, text="Start Mic", command=self.toggleMic)
        self.micButton.status = "close"
        self.micButton.pack(pady=10)

        self.is_recording = False

    def toggleMic(self):
        if self.micButton.status == "close":
            self.micButton.config(text="Close Mic")
            self.micButton.status = "open"
            self.startRecording()
        elif self.micButton.status == "open":
            self.micButton.config(text="Start Mic")
            self.micButton.status = "close"
            self.stopRecording()

    def startRecording(self):
        self.is_recording = True
        self.stream = sd.RawInputStream(dtype='int16', channels=1, callback=recordCallback, blocksize=1024)
        self.stream.start()  # Start the audio stream
        threading.Thread(target=self.record).start()

    def stopRecording(self):
        self.is_recording = False
        if self.stream:
            self.stream.stop()  # Stop the audio stream
            self.stream.close()  # Close the audio stream
            self.stream = None

    def record(self):
        while self.is_recording:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                recognizerResult = recognizer.Result()
                resultDict = json.loads(recognizerResult)
                if resultDict.get("text"):
                    print(f"Command recognized: {resultDict['text']}")
                    executeCommand(resultDict['text'])

    def closeApp(self):
        self.stopRecording()
        self.root.quit()
        sys.exit()
            

# list all audio devices known to your system
print("Display input/output devices")
print(sd.query_devices())


# get the samplerate - this is needed by the Kaldi recognizer
device_info = sd.query_devices(sd.default.device[0], 'input')
samplerate = int(device_info['default_samplerate'])

# display the default input device
print("===> Initial Default Device Number:{} Description: {}".format(sd.default.device[0], device_info))

# setup queue and callback function
q = queue.Queue()

def recordCallback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))
    
# build the model and recognizer objects.
print("===> Build the model and recognizer objects.  This will take a few minutes...")
model_path = vosk.Model(r"/usr/share/vosk/models/vosk-model-en-us-0.22")
recognizer = vosk.KaldiRecognizer(model_path, samplerate)
recognizer.SetWords(False)


print("===> Begin recording. Press Ctrl+C to stop the recording ")

def executeCommand(command):
    command = command.lower()
    print(f"Command received: {command}")
    
    try:
        # Open applications
        if "open firefox" in command:
            subprocess.run(["firefox"], check=True)
            print("Opening Firefox browser...")

        # Basic computer commands
        elif "open terminal" in command:
            subprocess.run(["gnome-terminal"], check=True)
            print("Opening terminal...")
        
        elif "shutdown" in command or "shut down" in command:
            subprocess.run(["shutdown", "now"], check=True)
            print("Shutting down...")
        
        elif "sleep" in command:
            subprocess.run(["systemctl", "suspend"])
            print("Sleeping...")

        elif "hibernate" in command:
            subprocess.run(["systemctl", "hibernate"])
            print("Hibernating computer...")

        elif "restart" in command:
            subprocess.run(["reboot"], check=True)
            print("Restarting...")
        
        elif "lock screen" in command:
            subprocess.run(["gnome-screensaver-command", "--lock"])
            print("Locking user...")

        elif "logout" in command or "log out" in command:
            subprocess.run(["gnome-session-quit", "--logout", "--no-prompt"])
            print("User logging out...")

        elif "volume up" in command:
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "10%+"], check=True)
            print("Increasing volume...")
        
        elif "volume down" in command:
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "10%-"], check=True)
            print("Decreasing volume...")

        elif "mute volume" in command:
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "100%-"], check=True)
            print("Muting volume...")
        
        elif "full volume" in command or "max volume" in command:
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "100%+"], check=True)
            print("Increasing volume...")
        
        elif "date" in command:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Current date and time: {now}")

        elif "set brightness" in command:
            brightness_value = re.search(r"set brightness to (\d+)", command)
            if brightness_value:
                brightness_value = int(brightness_value.group(1))
                subprocess.run(["xbacklight", "-set", f"{brightness_value}"])
                print(f"Setting brightness to {brightness_value}...")
            else:
                print("No brightness value detected.")

        elif "exit voice" in command:
            print("Closing voice command assistant...")
            app.closeApp()


        else:
            print("Command not recognized.")

    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceCommandWidget(root)
    print("run1")
    root.mainloop()
