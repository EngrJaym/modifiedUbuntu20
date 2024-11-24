import cv2
from pyzbar import pyzbar
import webbrowser
import subprocess
from tkinter import filedialog, messagebox, Tk, Button, Label
from PIL import Image, ImageTk

class QRCodeScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Scanner")
        self.root.geometry("800x600")

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not access the webcam.")
            self.root.destroy()
            return

        self.zoom_level = 1
        self.running = True
        self.last_scanned_qr = None  # Store the last scanned QR code to avoid duplicates

        # Create GUI elements
        self.label = Label(root)
        self.label.pack()

        self.qr_text_label = Label(root, text="QR Code Text: None", font=("Helvetica", 14))
        self.qr_text_label.pack(pady=20)

        self.btn_zoom_in = Button(root, text="Zoom In (+)", command=self.zoom_in)
        self.btn_zoom_in.pack(side="left", padx=10)

        self.btn_zoom_out = Button(root, text="Zoom Out (-)", command=self.zoom_out)
        self.btn_zoom_out.pack(side="left", padx=10)

        self.btn_scan_image = Button(root, text="Scan Image", command=self.scan_image_file)
        self.btn_scan_image.pack(side="left", padx=10)

        self.btn_exit = Button(root, text="Exit", command=self.on_closing)
        self.btn_exit.pack(side="left", padx=10)

        # Handle the close button
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.update_frame()

    def update_frame(self):
        if self.running:
            ret, frame = self.cap.read()
            if ret:
                # Apply zoom
                frame = self.zoom_camera(frame, self.zoom_level)

                # Scan QR codes in the frame
                self.scan_qr_code_from_camera(frame)

                # Convert frame for Tkinter display
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = ImageTk.PhotoImage(Image.fromarray(frame))
                self.label.imgtk = img
                self.label.configure(image=img)

            self.root.after(10, self.update_frame)

    def zoom_in(self):
        self.zoom_level += 0.1

    def zoom_out(self):
        self.zoom_level = max(0.1, self.zoom_level - 0.1)

    def scan_image_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a QR code image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if file_path:
            self.scan_qr_code_from_image(file_path)

    def scan_qr_code_from_camera(self, frame):
        qr_codes = pyzbar.decode(frame)
        for qr in qr_codes:
            (x, y, w, h) = qr.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            qr_data = qr.data.decode('utf-8')
            qr_type = qr.type
            text = f"{qr_type}: {qr_data}"
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Check if it's a duplicate QR code
            if qr_data == self.last_scanned_qr:
                continue
            self.last_scanned_qr = qr_data  # Update the last scanned QR code
            print("QR Code detected:", qr_data)

            # Update the QR code text label in the Tkinter window
            self.qr_text_label.config(text=f"QR Code Text: {qr_data}",fg="black", cursor="arrow")
            self.qr_text_label.unbind("<Button-1>")

            # Open URL in Firefox
            if qr_data.startswith("http://") or qr_data.startswith("https://"):
                self.qr_text_label.config(fg="blue", cursor="hand2")
                self.qr_text_label.bind("<Button-1>", lambda e: webbrowser.open(qr_data))
                #self.open_in_firefox(qr_data)

            # Connect to Wi-Fi
            if qr_data.startswith("WIFI:"):
                ssid = qr_data.split(";")[0].split(":")[2]
                password = qr_data.split(";")[2].split(":")[1]
                self.connect_to_wifi(ssid, password)            

    def scan_qr_code_from_image(self, image_path):
        image = cv2.imread(image_path)
        if image is None:
            print("Failed to load image")
            return

        qr_codes = pyzbar.decode(image)
        for qr in qr_codes:
            qr_data = qr.data.decode('utf-8')
            qr_type = qr.type
            print("QR Code detected in image:", qr_data)

            # Update the QR code text label in the Tkinter window
            self.qr_text_label.config(text=f"QR Code Text: {qr_data}")

            # Open URL in Firefox
            if qr_data.startswith("http://") or qr_data.startswith("https://"):
                self.open_in_firefox(qr_data)

            # Connect to Wi-Fi
            if qr_data.startswith("WIFI:"):
                ssid = qr_data.split(";")[0].split(":")[2]
                password = qr_data.split(";")[2].split(":")[1]
                self.connect_to_wifi(ssid, password)

    def zoom_camera(self, frame, zoom_factor):
        height, width = frame.shape[:2]
        new_width = int(width * zoom_factor)
        new_height = int(height * zoom_factor)
        zoomed_frame = cv2.resize(frame, (new_width, new_height))
        center_x, center_y = new_width // 2, new_height // 2
        cropped_frame = zoomed_frame[
            center_y - height // 2 : center_y + height // 2,
            center_x - width // 2 : center_x + width // 2
        ]
        return cropped_frame

    def open_in_firefox(self, url):
        webbrowser.get('firefox').open(url)

    def connect_to_wifi(self, ssid, password):
        command = f"nmcli dev wifi connect '{ssid}' password '{password}'"
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Connected to Wi-Fi network: {ssid}")
        except subprocess.CalledProcessError:
            print("Failed to connect to the Wi-Fi network.")

    def on_closing(self):
        if messagebox.askyesno("Warning", "Are you sure you want to exit?"):
            self.running = False
            self.cap.release()
            self.root.destroy()

if __name__ == "__main__":
    root = Tk()
    app = QRCodeScannerApp(root)
    root.mainloop()


