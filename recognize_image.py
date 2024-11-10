# USAGE
# python recognize.py --image path/to/image.jpg
# python recognize_image.py --image dataset\\aakash\\00000.png 
# dataset\modi\00000.png
# import libraries
import numpy as np
import argparse
import imutils
import pickle
import cv2
import os

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
        proba = preds[j]
        name = le.classes_[j]

        # Draw the bounding box of the face along with the associated probability
        text = "{}: {:.2f}%".format(name, proba * 100)
        y = startY - 10 if startY - 10 > 10 else startY + 10
        cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
        cv2.putText(image, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

    return image

def main():
    # Construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="input image path")
    args = vars(ap.parse_args())

    # Validate input image path
    if not os.path.exists(args["image"]):
        print("[ERROR] Input image path does not exist.")
        return

    # Load serialized face detector and embedding models
    proto_path = os.path.sep.join(['face_detection_model', "deploy.prototxt"])
    model_path = os.path.sep.join(['face_detection_model', "res10_300x300_ssd_iter_140000.caffemodel"])
    detector = load_face_detector(proto_path, model_path)

    embedder = load_face_embedder('openface_nn4.small2.v1.t7')

    # Load face recognition model and label encoder
    recognizer, le = load_recognizer_and_label_encoder('output/recognizer.pickle', 'output/le.pickle')

    # Load the input image, resize it, and detect faces
    image = cv2.imread(args["image"])
    image = imutils.resize(image, width=600)
    faces = detect_faces(image, detector)

    # Recognize and annotate faces in the image
    output_image = recognize_faces(image, faces, embedder, recognizer, le)

    # Show the output image
    cv2.imshow("Image", output_image)
    cv2.waitKey(0)

if __name__ == "__main__":
    main()
