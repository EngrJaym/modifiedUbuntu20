import queue
import sounddevice as sd
import vosk
import sys
import json
import subprocess
import datetime
import re
import threading
import os
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

class VoiceCommand:
    def __init__(self):
        self.is_recording = False
        self.stream = None

    def startRecording(self):
        self.is_recording = True
        self.stream = sd.RawInputStream(dtype='int16', channels=1, callback=recordCallback, blocksize=1024)
        self.stream.start()
        threading.Thread(target=self.record).start()

    def stopRecording(self):
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
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

    def toggleRecording(self):
        print(f"Recording:{self.is_recording}")
        if self.is_recording:
            self.stopRecording()
        else:
            self.startRecording()

    def closeApp(self, icon):
        self.stopRecording()
        icon.stop()

# list all audio devices known to your system
print("Display input/output devices")
print(sd.query_devices())

# get the samplerate - this is needed by the Kaldi recognizer
device_info = sd.query_devices(sd.default.device[0], 'input')
samplerate = int(device_info['default_samplerate'])

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

def executeCommand(command):
    command = command.lower()
    print(f"Command received: {command}")

    while True:
        try:
            # Open applications (your existing command cases)
            if "open firefox" in command:
                subprocess.run(["firefox"], check=True)
                print("Opening Firefox browser...")
            # Other command cases ...

            elif "open chrome" in command:
                subprocess.run(["google-chrome"], check=True)
                print("Opening Chrome browser...")

            elif "open visual studio code" in command or "open vscode" in command or "open vs code" in command:
                subprocess.run(["code"], check=True)

            elif "open rhythmbox" in command or "open rhythm box" in command:
                subprocess.run(["rhythmbox"], check=True)

            elif "open clip history" in command:      
                subprocess.run(["python3", "/opt/clipHistory/clipHistory.py"], check=True)

            elif "open theme switcher" in command:
                subprocess.run(["python3", "/opt/themeSwitch/themeSwitch.py"], check=True)

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
            elif "search file" in command:
                filename = re.search(r"search file (.*)", command)
                if filename:
                    subprocess.run(["find", "/", "-name", filename.group(1)], check=True)
                    print(f"Searching for file: {filename.group(1)}")
                else:
                    print("No file name detected.")

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
            elif "weather" in command or "whether" in command:
                subprocess.run(["curl", "wttr.in"], check=True)
                print("Fetching weather report...")

            # Miscellaneous commands
            elif "take screenshot" in command:
                subprocess.run(["gnome-screenshot"], check=True)
                print("Taking a screenshot...")

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

            elif "exit voice" in command:
                print("Closing voice command assistant...")
                app.closeApp()

        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")

        except Exception as e:
                print(f"An unexpected error occurred: {e}")
        finally:
            # Optionally handle cleanup or reset state
            print("Ready for the next command.")
        break
    
def create_image(is_recording):
    # Create a mic icon image
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Change the mic icon color based on recording state
    mic_color = (0, 255, 0) if is_recording else (255, 0, 0)  # Green if recording, Red if stopped

    # Draw mic base (circle)
    mic_center = (width // 2, height // 3)
    mic_radius = 16
    draw.ellipse(
        (mic_center[0] - mic_radius, mic_center[1] - mic_radius,
         mic_center[0] + mic_radius, mic_center[1] + mic_radius),
        fill=mic_color
    )

    # Draw mic handle (rectangle)
    handle_width = 10
    handle_height = 20
    handle_top = mic_center[1] + mic_radius
    draw.rectangle(
        (mic_center[0] - handle_width // 2, handle_top,
         mic_center[0] + handle_width // 2, handle_top + handle_height),
        fill=mic_color
    )

    # Draw mic stand (line)
    stand_height = 10
    stand_top = handle_top + handle_height
    draw.line(
        [(mic_center[0], stand_top), (mic_center[0], stand_top + stand_height)],
        fill=mic_color, width=3
    )

    return image

def on_quit(icon, item):
    pass

def toggle_voice_command(icon, _):
    app.toggleRecording()
    print(f"value of app is recording: {app.is_recording}")

    icon.icon = create_image(app.is_recording)


if __name__ == "__main__":
    app = VoiceCommand()
    print("speak")

    icon = pystray.Icon("VoiceCommand")
    icon.icon = create_image(app.is_recording) 
    icon.menu = pystray.Menu(
        item('Toggle Voice Command', toggle_voice_command)
    )
    icon.run()
