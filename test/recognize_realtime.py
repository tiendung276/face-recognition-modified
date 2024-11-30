import numpy as np
import imutils
import pickle
import cv2
import os
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import datetime

# Load models and utilities
def load_face_detector(proto_path, model_path):
    """Load the face detector model."""
    print("Loading Face Detector...")
    return cv2.dnn.readNetFromCaffe(proto_path, model_path)

def load_face_embedder(model_path):
    """Load the face embedding model."""
    print("Loading Face Recognizer...")
    return cv2.dnn.readNetFromTorch(model_path)

def load_recognizer_and_label_encoder(recognizer_path, le_path):
    """Load the face recognition model and label encoder."""
    with open(recognizer_path, "rb") as f:
        recognizer = pickle.load(f)
    with open(le_path, "rb") as f:
        le = pickle.load(f)
    return recognizer, le

# Face detection and recognition
def detect_faces(image, detector, min_confidence=0.5):
    """Detect faces in an image."""
    (h, w) = image.shape[:2]
    image_blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300),
                                       (104.0, 177.0, 123.0), swapRB=False, crop=False)
    detector.setInput(image_blob)
    detections = detector.forward()

    faces = []
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        # Filter out weak detections
        if confidence > min_confidence:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # Ensure bounding box is within image dimensions
            startX, startY = max(0, startX), max(0, startY)
            endX, endY = min(w, endX), min(h, endY)

            face = image[startY:endY, startX:endX]
            faces.append((face, (startX, startY, endX, endY)))

    return faces

def recognize_faces(image, faces, embedder, recognizer, le):
    """Recognize faces in the image and draw the results."""
    recognized = False
    for (face, (startX, startY, endX, endY)) in faces:
        (fH, fW) = face.shape[:2]

        # Ensure the face width and height are sufficiently large
        if fW < 20 or fH < 20:
            continue

        # Construct a blob for the face ROI
        face_blob = cv2.dnn.blobFromImage(face, 1.0 / 255, (96, 96),
                                          (0, 0, 0), swapRB=True, crop=False)
        embedder.setInput(face_blob)
        vec = embedder.forward()

        # Perform classification to recognize the face
        preds = recognizer.predict_proba(vec)[0]
        j = np.argmax(preds)
        proba = preds[j]
        name = le.classes_[j]

        # Draw the bounding box of the face along with the associated probability
        text = "{}: {:.2f}%".format(name, proba * 100)
        y = startY - 10 if startY - 10 > 10 else startY + 10
        cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
        cv2.putText(image, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

    return image


# Tkinter GUI
def start_recognition():
    # Load serialized face detector and embedding models
    proto_path = "C:\\Users\\tdun\\Documents\\QuanLyNhanSu\\face-recognition-using-opencv\\model\\face_detection_model\\deploy.prototxt"
    model_path = "C:\\Users\\tdun\\Documents\\QuanLyNhanSu\\face-recognition-using-opencv\\model\\face_detection_model\\res10_300x300_ssd_iter_140000.caffemodel"
    detector = load_face_detector(proto_path, model_path)

    embedder = load_face_embedder('C:\\Users\\tdun\\Documents\\QuanLyNhanSu\\face-recognition-using-opencv\\model\\face_detection_model\\openface_nn4.small2.v1.t7')
    recognizer, le = load_recognizer_and_label_encoder('C:\\Users\\tdun\\Documents\\QuanLyNhanSu\\face-recognition-using-opencv\\model\\embeddings.pickle', 'C:\\Users\\tdun\\Documents\\QuanLyNhanSu\\face-recognition-using-opencv\\model\\le.pickle')

    # Start video capture (webcam)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open webcam.")
        return

    start_time = datetime.datetime.now()
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture frame from webcam.")
            break

        # Resize frame for faster processing
        frame = imutils.resize(frame, width=600)
        
        # Detect faces in the frame
        faces = detect_faces(frame, detector)
        
        # Recognize faces in the frame
        output_frame = recognize_faces(frame, faces, embedder, recognizer, le)
        
        # Display the resulting frame
        cv2.imshow('Real-Time Face Recognition (Press "q" to quit)', output_frame)

        # Stop if the window is closed or 'q' is pressed or after a few seconds
        if cv2.getWindowProperty('Real-Time Face Recognition (Press "q" to quit)', cv2.WND_PROP_VISIBLE) < 1:
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if (datetime.datetime.now() - start_time).seconds > 5:  # Capture for a few seconds
            break

    # Release the webcam and close windows
    cap.release()
    cv2.destroyAllWindows()

# Create main tkinter window
def main():
    window = tk.Tk()
    window.title("Face Recognition Attendance System")
    window.geometry("400x200")

    lbl = tk.Label(window, text="Face Recognition Attendance System", font=("Arial", 16))
    lbl.pack(pady=20)

    start_btn = tk.Button(window, text="Start Recognition", command=start_recognition, font=("Arial", 14))
    start_btn.pack(pady=20)

    window.mainloop()

if __name__ == "__main__":
    main()
