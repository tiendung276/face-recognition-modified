import tkinter as tk
from tkinter import *
import os, cv2
import shutil
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import tkinter.font as font
import pyttsx3
import subprocess


# project module
import automaticAttendance as automaticAttendance

# engine = pyttsx3.init()
# engine.say("Welcome!")
# engine.say("Please browse through your options..")
# engine.runAndWait()


haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimagelabel_path = (
    "TrainingImageLabel\Trainner.yml"
)
trainimage_path = "TrainingImage"
if not os.path.exists(trainimage_path):
    os.makedirs(trainimage_path)

studentdetail_path = (
    "StudentDetails\studentdetails.csv"
)
attendance_path = "Attendance"

window = Tk()
window.title("Face recognizer")
window.geometry("1280x720")
window.configure(background="gray")

# to destroy screen
def del_sc1():
    sc1.destroy()

# error message for name and no
def err_screen():
    global sc1
    sc1 = tk.Tk()
    sc1.geometry("400x110")
    sc1.iconbitmap("AMS.ico")
    sc1.title("Warning!!")
    sc1.configure(background="gray")
    sc1.resizable(0, 0)
    tk.Label(
        sc1,
        text="Enrollment & Name required!!!",
        fg="yellow",
        bg="gray",
        font=("times", 20, " bold "),
    ).pack()
    tk.Button(
        sc1,
        text="OK",
        command=del_sc1,
        fg="yellow",
        bg="gray",
        width=9,
        height=1,
        activebackground="Red",
        font=("times", 20, " bold "),
    ).place(x=110, y=50)

def testVal(inStr, acttyp):
    if acttyp == "1":  # insert
        if not inStr.isdigit():
            return False
    return True


titl = tk.Label(
    window, text="Smart College!!", bg="gray", fg="green", font=("arial", 27),
)
titl.place(x=525, y=12)

a = tk.Label(
    window,
    text="Attendance Management System",
    bg="gray",
    fg="yellow",
    bd=10,
    font=("arial", 35),
)
a.pack()



vi = Image.open("UI_icons/verifyy.png")
v = ImageTk.PhotoImage(vi)
label3 = Label(window, image=v)
label3.image = v
label3.place(x=550, y=270)

def TakeImageUI():
    ImageUI = Tk()
    ImageUI.title("Take Student Image..")
    ImageUI.geometry("780x480")
    ImageUI.configure(background="gray")
    ImageUI.resizable(0, 0)
    titl = tk.Label(ImageUI, bg="gray", relief=RIDGE, bd=10, font=("arial", 35))
    titl.pack(fill=X)
    # image and title
    titl = tk.Label(
        ImageUI, text="Register Your Face", bg="gray", fg="green", font=("arial", 30),
    )
    titl.place(x=270, y=12)

    # heading
    a = tk.Label(
        ImageUI,
        text="Enter the details",
        bg="gray",
        fg="yellow",
        bd=10,
        font=("arial", 24),
    )
    a.place(x=280, y=75)

    # ER no
    lbl1 = tk.Label(
        ImageUI,
        text="Enrollment No",
        width=10,
        height=2,
        bg="gray",
        fg="yellow",
        bd=5,
        relief=RIDGE,
        font=("times new roman", 12),
    )
    lbl1.place(x=120, y=130)
    txt1 = tk.Entry(
        ImageUI,
        width=17,
        bd=5,
        validate="key",
        bg="gray",
        fg="yellow",
        relief=RIDGE,
        font=("times", 25, "bold"),
    )
    txt1.place(x=250, y=130)
    txt1["validatecommand"] = (txt1.register(testVal), "%P", "%d")

    # name
    lbl2 = tk.Label(
        ImageUI,
        text="Name",
        width=10,
        height=2,
        bg="gray",
        fg="yellow",
        bd=5,
        relief=RIDGE,
        font=("times new roman", 12),
    )
    lbl2.place(x=120, y=200)
    txt2 = tk.Entry(
        ImageUI,
        width=17,
        bd=5,
        bg="gray",
        fg="yellow",
        relief=RIDGE,
        font=("times", 25, "bold"),
    )
    txt2.place(x=250, y=200)

    lbl3 = tk.Label(
        ImageUI,
        text="Notification",
        width=10,
        height=2,
        bg="gray",
        fg="yellow",
        bd=5,
        relief=RIDGE,
        font=("times new roman", 12),
    )
    lbl3.place(x=120, y=270)

    message = tk.Label(
        ImageUI,
        text="",
        width=32,
        height=2,
        bd=5,
        bg="gray",
        fg="yellow",
        relief=RIDGE,
        font=("times", 12, "bold"),
    )
    message.place(x=250, y=270)

    def take_image(num_images = 20):
        # Create directory for the user if it doesn't exist
        user_id = txt1.get()
        username = txt2.get()
        
        dataset_path = os.path.join("dataset", username+"_"+user_id)
        if not os.path.exists(dataset_path):
            os.makedirs(dataset_path)

        cap = cv2.VideoCapture(0)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1200)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
        cap.set(cv2.CAP_PROP_FPS, 30)

        count = 0

        print(f"[INFO] Starting to capture images for user: {username}")
        while count < num_images:
            # Capture frame-by-frame
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] Failed to capture image from webcam.")
                break

            # Allow more time for better image quality
            time.sleep(0.1)
            # Display the resulting frame
            cv2.imshow('Capture Images (Press "q" to quit)', frame)

            # Save the current frame as an image file
            image_path = os.path.join(dataset_path, f"{str(count).zfill(5)}.png")
            cv2.imwrite(image_path, frame)
            count += 1

            print(f"[INFO] Captured image {count}/{num_images}")

            # Press 'q' to quit capturing images early
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the webcam and close windows
        cap.release()
        cv2.destroyAllWindows()
        print(f"[INFO] Completed capturing {count} images for user: {username}")

    # take Image button
    # image
    takeImg = tk.Button(
        ImageUI,
        text="Take Image",
        command=take_image,
        bd=10,
        font=("times new roman", 18),
        bg="gray",
        fg="yellow",
        height=2,
        width=12,
        relief=RIDGE,
    )
    takeImg.place(x=130, y=350)

    def train_image():
        try:
            subprocess.run(["python", "train_model.py"], check=True)
        except subprocess.CalledProcessError as e:
            print("An error occurred while training the model:", e)

    trainImg = tk.Button(
        ImageUI,
        text="Train Image",
        command=train_image,
        bd=10,
        font=("times new roman", 18),
        bg="gray",
        fg="yellow",
        height=2,
        width=12,
        relief=RIDGE,
    )
    trainImg.place(x=360, y=350)

r = tk.Button(
    window,
    text="Register a new student",
    command=TakeImageUI,
    bd=10,
    font=("times new roman", 16),
    bg="gray",
    fg="yellow",
    height=2,
    width=17,
)
r.place(x=100, y=520)

def automatic_attendance():
    automaticAttendance.start_recognition()

r = tk.Button(
    window,
    text="Take Attendance",
    command=automatic_attendance,
    bd=10,
    font=("times new roman", 16),
    bg="gray",
    fg="yellow",
    height=2,
    width=17,
)
r.place(x=550, y=520)

def view_attendance():
    return 1
r = tk.Button(
    window,
    text="View Attendance",
    command=view_attendance,
    bd=10,
    font=("times new roman", 16),
    bg="gray",
    fg="yellow",
    height=2,
    width=17,
)
r.place(x=980, y=520)


window.mainloop()
