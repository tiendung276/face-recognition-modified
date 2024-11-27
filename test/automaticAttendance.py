import numpy as np
import imutils
import pickle
import cv2
import os
import pandas as pd
import datetime

# Global attendance list to track users who have already taken attendance
attendance_list = {}

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
        name = le.classes_[j]

        # Extract ID and username from recognized name (format should be 'UserName_ID')
        if '_' in name:
            username, user_id = name.rsplit('_', 1)
        else:
            username = name
            user_id = name

        # Record attendance if not already recorded for today and name is not 'unknown'
        today = datetime.datetime.now().date()
        if name.lower() != 'unknown' and (user_id not in attendance_list or attendance_list[user_id] != today):
            if not check_existing_attendance(user_id, today):
                attendance_list[user_id] = today
                record_attendance(user_id, username)
                print(f"Attendance recorded for {username} ({user_id})")
            else:
                print(f"{username} ({user_id}) has already taken attendance today.")
        elif user_id in attendance_list and attendance_list[user_id] == today:
            # Print message if user attempts to take attendance multiple times
            print(f"{username} ({user_id}) has already taken attendance today.")

    return image

# Check if attendance is already recorded
def check_existing_attendance(user_id, date):
    """Check if attendance for the given user ID and date is already recorded."""
    attendance_file = 'Attendance/attendance.csv'
    if os.path.exists(attendance_file):
        df = pd.read_csv(attendance_file)
        if 'ID' in df.columns and 'AttendanceDate' in df.columns:
            df['AttendanceDate'] = pd.to_datetime(df['AttendanceDate']).dt.date
            existing = df[(df['ID'] == user_id) & (df['AttendanceDate'] == date)]
            return not existing.empty
    return False

def record_attendance(user_id, username):
    """Record attendance in a CSV file."""
    if not os.path.exists('Attendance'):
        os.makedirs('Attendance')
    attendance_file = 'Attendance/attendance.csv'
    now = datetime.datetime.now()
    date_str = now.strftime('%Y-%m-%d')

    # Check if record already exists before appending
    if not check_existing_attendance(user_id, now.date()):
        # Append attendance record
        df = pd.DataFrame([[user_id, username, date_str]], columns=['ID', 'Name', 'AttendanceDate'])
        if os.path.exists(attendance_file):
            df.to_csv(attendance_file, mode='a', header=False, index=False)
        else:
            df.to_csv(attendance_file, mode='w', header=True, index=False)

def load_existing_attendance():
    """Load existing attendance records into the global attendance list."""
    global attendance_list
    attendance_file = 'Attendance/attendance.csv'
    if os.path.exists(attendance_file):
        df = pd.read_csv(attendance_file)
        df['AttendanceDate'] = pd.to_datetime(df['AttendanceDate']).dt.date
        today = datetime.datetime.now().date()
        existing_attendance = df[df['AttendanceDate'] == today]
        for _, row in existing_attendance.iterrows():
            attendance_list[row['ID']] = row['AttendanceDate']

def start_recognition():
    # Load serialized face detector and embedding models
    proto_path = os.path.sep.join(['face_detection_model', "deploy.prototxt"])
    model_path = os.path.sep.join(['face_detection_model', "res10_300x300_ssd_iter_140000.caffemodel"])
    detector = load_face_detector(proto_path, model_path)

    embedder = load_face_embedder('face_detection_model/openface_nn4.small2.v1.t7')
    recognizer, le = load_recognizer_and_label_encoder('output/recognizer.pickle', 'output/le.pickle')

    # Load existing attendance list to prevent multiple entries on the same day
    load_existing_attendance()

    # Start video capture (webcam)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    picture_count = 0

    while picture_count < 3:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame from webcam.")
            break

        # Resize frame for faster processing
        frame = imutils.resize(frame, width=600)
        
        # Detect faces in the frame
        faces = detect_faces(frame, detector)
        
        # Recognize faces in the frame
        recognize_faces(frame, faces, embedder, recognizer, le)
        picture_count += 1

    cap.release()
    print("Attendance process completed.")

if __name__ == "__main__":
    start_recognition()