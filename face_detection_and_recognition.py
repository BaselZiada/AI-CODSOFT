import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import os

video_capture = None
image = None
detection_color = (0, 255, 0)  # Default color for detection rectangles
scale_factor = 1.1
min_neighbors = 5
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
recording = False
out = None

# Function to perform face detection on images
def detect_faces_image():
    global image
    global canvas
    global detection_color
    global scale_factor
    global min_neighbors

    file_path = filedialog.askopenfilename()

    if file_path:
        image = cv2.imread(file_path)
        image = cv2.resize(image, (340, 380))

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=scale_factor, minNeighbors=min_neighbors, minSize=(30, 30))

        num_faces = len(faces)
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), detection_color, 2)

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_tk = ImageTk.PhotoImage(image_pil)

        canvas.config(image=image_tk)
        canvas.image = image_tk

        result_label.config(text=f'Faces Detected: {num_faces}', fg="#000", bg="#d6cadd")
        root.title(f"Advanced Face Detection GUI - Faces Detected: {num_faces}")

# Function to perform face detection from the camera
def detect_faces_camera():
    global video_capture

    if video_capture is not None:
        video_capture.release()

    video_capture = cv2.VideoCapture(0)
    video_capture.set(3, 320)
    video_capture.set(4, 240)

    detect_faces()

# Function to continuously capture frames and perform face detection
def detect_faces():
    global image, video_capture, result_label, root

    if video_capture is not None:
        ret, frame = video_capture.read()

        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=scale_factor, minNeighbors=min_neighbors, minSize=(30, 30))

            num_faces = len(faces)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), detection_color, 2)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            frame_tk = ImageTk.PhotoImage(frame_pil)

            canvas.config(image=frame_tk)
            canvas.image = frame_tk

            result_label.config(text=f'Faces Detected: {num_faces}')
            root.title(f"Advanced Face Detection GUI - Faces Detected: {num_faces}")

            root.after(10, detect_faces)

# Function to save the image with detected faces
def save_image():
    global image
    if image is not None:
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
        if file_path:
            cv2.imwrite(file_path, image)
            messagebox.showinfo("Save Image", "Image saved successfully!")
    else:
        messagebox.showwarning("Save Image", "No image to save.")

# Function to show help information
def show_help():
    messagebox.showinfo("Help", "1. Click 'Open Image' to select an image file for face detection.\n"
                                "2. Click 'Camera Detection' to start detecting faces from your webcam.\n"
                                "3. Click 'Save Image' to save the image with detected faces.\n"
                                "4. Click 'Change Detection Color' to select a color for detection rectangles.\n"
                                "5. Use sliders to adjust detection parameters.\n"
                                "6. Click 'Record Video' to start/stop recording the video stream.\n"
                                "7. Click 'Apply Filter' to apply filters to the detected image.\n"
                                "8. Click 'Save Stats' to save detection statistics.")

# Function to change detection rectangle color
def change_detection_color():
    global detection_color
    color = colorchooser.askcolor(title="Choose Detection Color")[1]
    if color:
        detection_color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))

# Function to update scale factor
def update_scale_factor(value):
    global scale_factor
    scale_factor = float(value)

# Function to update min neighbors
def update_min_neighbors(value):
    global min_neighbors
    min_neighbors = int(value)

# Function to start/stop video recording
def toggle_recording():
    global video_capture, recording, out

    if recording:
        recording = False
        out.release()
        record_button.config(text="Start Recording")
        status_bar.config(text="Recording stopped")
    else:
        if video_capture is None:
            detect_faces_camera()
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        file_path = filedialog.asksaveasfilename(defaultextension=".avi", filetypes=[("AVI files", "*.avi")])
        if file_path:
            out = cv2.VideoWriter(file_path, fourcc, 20.0, (int(video_capture.get(3)), int(video_capture.get(4))))
            recording = True
            record_button.config(text="Stop Recording")
            status_bar.config(text="Recording...")

# Function to apply image filters
def apply_filter():
    global image
    if image is not None:
        filter_choice = filter_var.get()
        if filter_choice == "Grayscale":
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif filter_choice == "Sepia":
            sepia_filter = np.array([[0.272, 0.534, 0.131],
                                     [0.349, 0.686, 0.168],
                                     [0.393, 0.769, 0.189]])
            image = cv2.transform(image, sepia_filter)
        else:
            messagebox.showwarning("Filter", "Please select a valid filter.")
            return

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_tk = ImageTk.PhotoImage(image_pil)

        canvas.config(image=image_tk)
        canvas.image = image_tk

# Function to save detection statistics
def save_stats():
    global scale_factor, min_neighbors
    num_faces = result_label.cget("text").split(': ')[-1]
    stats = f"Detection Parameters:\nScale Factor: {scale_factor}\nMin Neighbors: {min_neighbors}\nFaces Detected: {num_faces}"

    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, 'w') as file:
            file.write(stats)
        messagebox.showinfo("Save Stats", "Statistics saved successfully!")

# Function to toggle between light and dark themes
def toggle_theme():
    if root.cget("bg") == "#f0f0f5":
        root.configure(bg="#1e1e1e")
        content_frame.configure(bg="#1e1e1e")
        detection_frame.configure(bg="#1e1e1e", fg="#cfcfcf")
        result_label.configure(bg="#1e1e1e", fg="#cfcfcf")
        status_bar.configure(bg="#3a3d5c", fg="white")
        for widget in sidebar.winfo_children():
            widget.configure(bg="#282a36", fg="white", activebackground="#44475a", activeforeground="white")
    else:
        root.configure(bg="#f0f0f5")
        content_frame.configure(bg="#f0f0f5")
        detection_frame.configure(bg="#f0f0f5", fg="#22223b")
        result_label.configure(bg="#f0f0f5", fg="#22223b")
        status_bar.configure(bg="#007acc", fg="white")
        for widget in sidebar.winfo_children():
            widget.configure(bg="#22223b", fg="white", activebackground="#3a3d5c", activeforeground="white")

# Create the main tkinter window
root = tk.Tk()
root.title("Advanced Face Detection GUI")
root.geometry("1000x800")
root.configure(bg="#f0f0f5")  # Light grey background

# Header Label
header_label = tk.Label(root, text="    Face Recognition (Beso)     ", font=("Helvetica", 24, "bold"), bg="#f0f0f5", fg="#22223b", pady=10)
header_label.pack(pady=(10, 0))

# Sidebar styling
sidebar = tk.Frame(root, bg="#4a4e69", width=220, padx=15, pady=15)
sidebar.pack(side=tk.LEFT, fill=tk.Y)

# Button style updates with modern fonts and colors
button_style = {
    "font": ("Helvetica", 14, "bold"),
    "fg": "white",
    "bg": "#22223b",
    "activebackground": "#3a3d5c",
    "activeforeground": "white",
    "relief": tk.FLAT,
    "bd": 0,
    "highlightthickness": 0,
    "padx": 10,
    "pady": 10
}

open_button = tk.Button(sidebar, text="Open Image", command=detect_faces_image, **button_style)
open_button.pack(fill=tk.X, pady=10)

camera_button = tk.Button(sidebar, text="Camera Detection", command=detect_faces_camera, **button_style)
camera_button.pack(fill=tk.X, pady=10)

save_button = tk.Button(sidebar, text="Save Image", command=save_image, **button_style)
save_button.pack(fill=tk.X, pady=10)

color_button = tk.Button(sidebar, text="Change Detection Color", command=change_detection_color, **button_style)
color_button.pack(fill=tk.X, pady=10)

record_button = tk.Button(sidebar, text="Start Recording", command=toggle_recording, **button_style)
record_button.pack(fill=tk.X, pady=10)

apply_filter_button = tk.Button(sidebar, text="Apply Filter", command=apply_filter, **button_style)
apply_filter_button.pack(fill=tk.X, pady=10)

stats_button = tk.Button(sidebar, text="Save Stats", command=save_stats, **button_style)
stats_button.pack(fill=tk.X, pady=10)

theme_button = tk.Button(sidebar, text="Toggle Theme", command=toggle_theme, **button_style)
theme_button.pack(fill=tk.X, pady=10)

help_button = tk.Button(sidebar, text="Help", command=show_help, **button_style)
help_button.pack(fill=tk.X, pady=10)

# Content frame updates
content_frame = tk.Frame(root, bg="#f0f0f5", padx=10, pady=10)
content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

canvas = tk.Label(content_frame, bg="#dfe7fd")
canvas.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

result_label = tk.Label(content_frame, text='', font=('Helvetica', 20, 'bold'), fg="#22223b", bg="#f0f0f5", padx=10, pady=10)
result_label.pack(pady=20)

# Detection Settings Frame
detection_frame = tk.LabelFrame(content_frame, text="Detection Settings", font=("Helvetica", 16, "bold"), bg="#f0f0f5", fg="#22223b", padx=10, pady=10)
detection_frame.pack(pady=20)

scale_label = tk.Label(detection_frame, text="Scale Factor", font=("Helvetica", 14), bg="#f0f0f5")
scale_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

scale_slider = tk.Scale(detection_frame, from_=1.01, to=2.0, resolution=0.01, orient=tk.HORIZONTAL, command=update_scale_factor, bg="#dfe7fd")
scale_slider.set(scale_factor)
scale_slider.grid(row=0, column=1, padx=10, pady=5)

neighbors_label = tk.Label(detection_frame, text="Min Neighbors", font=("Helvetica", 14), bg="#f0f0f5")
neighbors_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

neighbors_slider = tk.Scale(detection_frame, from_=1, to=20, orient=tk.HORIZONTAL, command=update_min_neighbors, bg="#dfe7fd")
neighbors_slider.set(min_neighbors)
neighbors_slider.grid(row=1, column=1, padx=10, pady=5)

# Filter Selection
filter_var = tk.StringVar(value="None")

filter_frame = tk.LabelFrame(content_frame, text="Filter Selection", font=("Helvetica", 16, "bold"), bg="#f0f0f5", fg="#22223b", padx=10, pady=10)
filter_frame.pack(pady=20)

grayscale_rb = tk.Radiobutton(filter_frame, text="Grayscale", variable=filter_var, value="Grayscale", font=("Helvetica", 14), bg="#f0f0f5")
grayscale_rb.pack(anchor=tk.W)

sepia_rb = tk.Radiobutton(filter_frame, text="Sepia", variable=filter_var, value="Sepia", font=("Helvetica", 14), bg="#f0f0f5")
sepia_rb.pack(anchor=tk.W)

# Status Bar
status_bar = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#007acc", fg="white")
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Start the main loop
root.mainloop()
