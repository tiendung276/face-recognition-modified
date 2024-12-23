# import libraries
from imutils import paths
import numpy as np
import imutils
import pickle
import cv2
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC

# create output directory if it doesn't exist
if not os.path.exists("model"):
    os.makedirs("model")

# load serialized face detector
print("Loading Face Detector...")
proto_path = "C:\\Users\\tdun\\Documents\\QuanLyNhanSu\\face-recognition-using-opencv\\model\\face_detection_model\\deploy.prototxt"
model_path = "C:\\Users\\tdun\\Documents\\QuanLyNhanSu\\face-recognition-using-opencv\\model\\face_detection_model\\res10_300x300_ssd_iter_140000.caffemodel"
embedder_path = "C:\\Users\\tdun\\Documents\\QuanLyNhanSu\\face-recognition-using-opencv\\model\\face_detection_model\\openface_nn4.small2.v1.t7"
recognizer_path = "C:\\Users\\tdun\\Documents\\QuanLyNhanSu\\face-recognition-using-opencv\\model\\embeddings.pickle"
le_path = "C:\\Users\\tdun\\Documents\\QuanLyNhanSu\\face-recognition-using-opencv\\model\\le.pickle"
detector = cv2.dnn.readNetFromCaffe(proto_path, model_path)

# load serialized face embedding model
print("Loading Face Recognizer...")
embedder = cv2.dnn.readNetFromTorch(embedder_path)

# grab the paths to the input images in our dataset
print("Quantifying Faces...")
imagePaths = list(paths.list_images("dataset"))

# initialize our lists of extracted facial embeddings and corresponding people names
knownEmbeddings = []
knownNames = []

# initialize the total number of faces processed
total = 0

# loop over the image paths
for (i, imagePath) in enumerate(imagePaths):
    if (i % 50 == 0):
        print("Processing image {}/{}".format(i, len(imagePaths)))
    name = imagePath.split(os.path.sep)[-2]

    # load the image, resize it to have a width of 600 pixels (while maintaining the aspect ratio), and then grab the image dimensions
    image = cv2.imread(imagePath)
    image = imutils.resize(image, width=600)
    (h, w) = image.shape[:2]

    # construct a blob from the image
    imageBlob = cv2.dnn.blobFromImage(
        cv2.resize(image, (300, 300)), 1.0, (300, 300),
        (104.0, 177.0, 123.0), swapRB=False, crop=False)

    # apply OpenCV's deep learning-based face detector to localize faces in the input image
    detector.setInput(imageBlob)
    detections = detector.forward()

    # ensure at least one face was found
    if len(detections) == 0:
        print(f"No face detected in {imagePath}")
        continue

    # we're making the assumption that each image has only ONE face, so find the bounding box with the largest probability
    i = np.argmax(detections[0, 0, :, 2])
    confidence = detections[0, 0, i, 2]

    # ensure that the detection with the largest probability also meets our minimum probability test (thus helping filter out weak detections)
    if confidence > 0.5:
        # compute the (x, y)-coordinates of the bounding box for the face
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")

        # ensure bounding box is within image dimensions
        startX, startY = max(0, startX), max(0, startY)
        endX, endY = min(w, endX), min(h, endY)

        # extract the face ROI and grab the ROI dimensions
        face = image[startY:endY, startX:endX]
        (fH, fW) = face.shape[:2]

        # ensure the face width and height are sufficiently large
        if fW < 20 or fH < 20:
            continue

        # construct a blob for the face ROI, then pass the blob through our face embedding model to obtain the 128-d quantification of the face
        faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,
            (96, 96), (0, 0, 0), swapRB=True, crop=False)
        embedder.setInput(faceBlob)
        vec = embedder.forward()

        # add the name of the person + corresponding face embedding to their respective lists
        knownNames.append(name)
        knownEmbeddings.append(vec.flatten())
        total += 1

# dump the facial embeddings + names to disk
print("[INFO] serializing {} encodings...".format(total))
data = {"embeddings": knownEmbeddings, "names": knownNames}
with open("model/embeddings.pickle", "wb") as f:
    pickle.dump(data, f)

# load the face embeddings
embeddings_path = "model/embeddings.pickle"
print(f"[INFO] loading face embeddings from {embeddings_path}...")
with open(embeddings_path, "rb") as f:
    data = pickle.load(f)

# encode the labels
print("[INFO] encoding labels...")
le = LabelEncoder()
labels = le.fit_transform(data["names"])

print("[INFO] training model...")
recognizer = SVC(C=1.0, kernel="linear", probability=True)
recognizer.fit(data["embeddings"], labels)

# write the actual face recognition model to disk
recognizer_path = "model/recognizer.pickle"
print(f"[INFO] saving recognizer model to {recognizer_path}...")
with open(recognizer_path, "wb") as f:
    pickle.dump(recognizer, f)

# write the label encoder to disk
le_path = "model/le.pickle"
print(f"[INFO] saving label encoder to {le_path}...")
with open(le_path, "wb") as f:
    pickle.dump(le, f)

print("[INFO] Model training complete.")
