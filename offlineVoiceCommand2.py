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

class VoiceCommand:
    def __init__(self):
        self.startRecording()
        self.is_recording = True

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
model_path = vosk.Model(r"/usr/share/vosk/models/vosk-model-en-us-0.42")
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

        elif "open chrome" in command:
            subprocess.run(["google-chrome"], check=True)
            print("Opening Chrome browser...")

        elif "open terminal" in command:
            subprocess.run(["gnome-terminal"], check=True)
            print("Opening terminal...")

        elif "open text editor" in command:
            subprocess.run(["gedit"], check=True)
            print("Opening text editor...")

        elif "open file manager" in command:
            subprocess.run(["nautilus"], check=True)
            print("Opening file manager...")

        # Basic computer commands
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
            print("Locking screen...")

        elif "logout" in command or "log out" in command:
            subprocess.run(["gnome-session-quit", "--logout", "--no-prompt"])
            print("Logging out...")

        # Volume control
        elif "volume up" in command:
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "10%+"], check=True)
            print("Increasing volume...")

        elif "volume down" in command:
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "10%-"], check=True)
            print("Decreasing volume...")

        elif "mute volume" in command:
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "100%-"], check=True)
            print("Muting volume...")

        elif "max volume" in command or "full volume" in command:
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "100%+"], check=True)
            print("Setting volume to maximum...")

        # System information
        elif "date" in command:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Current date and time: {now}")

        elif "battery status" in command:
            subprocess.run(["acpi", "-b"], check=True)
            print("Getting battery status...")

        elif "cpu usage" in command:
            subprocess.run(["top", "-n", "1", "-b", "|", "head", "-n", "10"], check=True)
            print("Getting CPU usage...")

        elif "memory usage" in command:
            subprocess.run(["free", "-h"], check=True)
            print("Getting memory usage...")

        # Network commands
        elif "wifi status" in command:
            subprocess.run(["nmcli", "dev", "wifi"], check=True)
            print("Checking WiFi status...")

        elif "connect to wifi" in command:
            ssid = re.search(r"connect to wifi (.*)", command)
            if ssid:
                wifi_name = ssid.group(1)
                subprocess.run(["nmcli", "dev", "wifi", "connect", wifi_name], check=True)
                print(f"Connecting to WiFi: {wifi_name}")
            else:
                print("No WiFi name detected.")

        elif "disconnect wifi" in command:
            subprocess.run(["nmcli", "dev", "disconnect"], check=True)
            print("Disconnecting WiFi...")

        elif "enable wifi" in command:
            subprocess.run(["nmcli", "radio", "wifi", "on"], check=True)
            print("Enabling WiFi...")

        elif "disable wifi" in command:
            subprocess.run(["nmcli", "radio", "wifi", "off"], check=True)
            print("Disabling WiFi...")

        # File management commands
        elif "create folder" in command:
            folder_name = re.search(r"create folder (.*)", command)
            if folder_name:
                folder_name = folder_name.group(1)
                subprocess.run(["mkdir", folder_name], check=True)
                print(f"Creating folder: {folder_name}")
            else:
                print("No folder name detected.")

        elif "delete file" in command:
            file_name = re.search(r"delete file (.*)", command)
            if file_name:
                file_name = file_name.group(1)
                subprocess.run(["rm", file_name], check=True)
                print(f"Deleting file: {file_name}")
            else:
                print("No file name detected.")

        elif "move file" in command:
            files = re.findall(r"move file (.*) to (.*)", command)
            if files:
                source, destination = files[0]
                subprocess.run(["mv", source, destination], check=True)
                print(f"Moving file: {source} to {destination}")
            else:
                print("No source or destination file path detected.")

        elif "copy file" in command:
            files = re.findall(r"copy file (.*) to (.*)", command)
            if files:
                source, destination = files[0]
                subprocess.run(["cp", source, destination], check=True)
                print(f"Copying file: {source} to {destination}")
            else:
                print("No source or destination file path detected.")

        elif "open file" in command:
            file_name = re.search(r"open file (.*)", command)
            if file_name:
                subprocess.run(["xdg-open", file_name], check=True)
                print(f"Opening file: {file_name}")
            else:
                print("No file name detected.")

        # Web browsing control
        elif "search google" in command:
            query = re.search(r"search google (.*)", command)
            if query:
                subprocess.run(["firefox", f"https://www.google.com/search?q={query.group(1)}"], check=True)
                print(f"Searching Google for: {query.group(1)}")
            else:
                print("No search query detected.")

        # Weather report
        elif "weather" in command:
            subprocess.run(["curl", "wttr.in"], check=True)
            print("Fetching weather report...")

        # Miscellaneous commands
        elif "open youtube" in command:
            subprocess.run(["firefox", "https://www.youtube.com"], check=True)
            print("Opening YouTube...")

        elif "play music" in command:
            subprocess.run(["rhythmbox", "--play"], check=True)
            print("Playing music...")

        elif "pause music" in command:
            subprocess.run(["rhythmbox", "--pause"], check=True)
            print("Pausing music...")

        elif "next track" in command:
            subprocess.run(["rhythmbox", "--next"], check=True)
            print("Skipping to next track...")

        elif "previous track" in command:
            subprocess.run(["rhythmbox", "--previous"], check=True)
            print("Going to previous track...")

        elif "open calculator" in command:
            subprocess.run(["gnome-calculator"], check=True)
            print("Opening calculator...")

        # Exit voice assistant
        elif "exit voice" in command:
            print("Closing voice command assistant...")
            app.closeApp()

        else:
            print("Command not recognized.")

    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")



if __name__ == "__main__":
    app = VoiceCommand()
    print("speak now")
