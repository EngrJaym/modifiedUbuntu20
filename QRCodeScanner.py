import cv2
from pyzbar import pyzbar
import webbrowser
import subprocess
import os
from tkinter import filedialog
import tkinter as tk

zoom_level = 1  # Initial zoom level

def open_in_firefox(url):
    webbrowser.get('firefox').open(url)

def connect_to_wifi(ssid, password):
    command = f"nmcli dev wifi connect '{ssid}' password '{password}'"
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Connected to Wi-Fi network: {ssid}")
    except subprocess.CalledProcessError:
        print("Failed to connect to the Wi-Fi network.")

def zoom_camera(frame, zoom_factor):
    height, width = frame.shape[:2]
    new_width = int(width * zoom_factor)
    new_height = int(height * zoom_factor)
    zoomed_frame = cv2.resize(frame, (new_width, new_height))
    center_x, center_y = new_width // 2, new_height // 2
    cropped_frame = zoomed_frame[center_y - height // 2 : center_y + height // 2, center_x - width // 2 : center_x + width // 2]
    return cropped_frame

def scan_qr_code_from_camera(frame):
    qr_codes = pyzbar.decode(frame)
    for qr in qr_codes:
        (x, y, w, h) = qr.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        qr_data = qr.data.decode('utf-8')
        qr_type = qr.type
        text = f"{qr_type}: {qr_data}"
        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        print("QR Code detected:", qr_data)

        # Open URL in Firefox
        if qr_data.startswith("http://") or qr_data.startswith("https://"):
            open_in_firefox(qr_data)

        # Connect to Wi-Fi
        if qr_data.startswith("WIFI:"):
            ssid = qr_data.split(";")[0].split(":")[2]
            password = qr_data.split(";")[2].split(":")[1]
            connect_to_wifi(ssid, password)

def scan_qr_code_from_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print("Failed to load image")
        return

    qr_codes = pyzbar.decode(image)
    for qr in qr_codes:
        qr_data = qr.data.decode('utf-8')
        qr_type = qr.type
        print("QR Code detected in image:", qr_data)

        # Open URL in Firefox
        if qr_data.startswith("http://") or qr_data.startswith("https://"):
            open_in_firefox(qr_data)

        # Connect to Wi-Fi
        if qr_data.startswith("WIFI:"):
            ssid = qr_data.split(";")[0].split(":")[2]
            password = qr_data.split(";")[2].split(":")[1]
            connect_to_wifi(ssid, password)

def open_file_dialog_and_scan():
    root = tk.Tk()
    root.withdraw()  # Hide the Tkinter root window
    file_path = filedialog.askopenfilename(title="Select a QR code image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    if file_path:
        print(f"Scanning QR code from: {file_path}")
        scan_qr_code_from_image(file_path)

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not access the webcam.")
        return

    mode = 'camera'  # Start in camera mode
    global zoom_level

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break

        # Apply zoom
        frame = zoom_camera(frame, zoom_level)

        if mode == 'camera':
            # Scan QR code from the camera feed
            scan_qr_code_from_camera(frame)

        # Display the frame (either camera or image scan)
        cv2.imshow("QR Code Scanner", frame)

        # Handle keypresses
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):  # Press 'q' to quit
            break
        elif key == ord('+'):  # Press '+' to zoom in
            zoom_level += 0.1
        elif key == ord('-'):  # Press '-' to zoom out
            zoom_level = max(0.1, zoom_level - 0.1)
        elif key == ord('f'):  # Press 'f' to open file dialog
            mode = 'file'  # Switch to file scanning mode
            open_file_dialog_and_scan()
            mode = 'camera'  # After file scanning, go back to camera mode

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
