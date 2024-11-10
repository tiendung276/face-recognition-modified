# USAGE
# python train_model.py --embeddings output/embeddings.pickle --recognizer output/recognizer.pickle --le output/le.pickle

# import the necessary packages
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import argparse
import pickle
import os

# create output directory if it doesn't exist
if not os.path.exists("output"):
    os.makedirs("output")

# load the face embeddings
print("[INFO] loading face embeddings...")
with open("output/embeddings.pickle", "rb") as f:
    data = pickle.load(f)

# encode the labels
print("[INFO] encoding labels...")
le = LabelEncoder()
labels = le.fit_transform(data["names"])

# train the model used to accept the 128-d embeddings of the face and
# then produce the actual face recognition
print("[INFO] training model...")
recognizer = SVC(C=1.0, kernel="linear", probability=True)
recognizer.fit(data["embeddings"], labels)

# write the actual face recognition model to disk
with open("output/recognizer.pickle", "wb") as f:
    pickle.dump(recognizer, f)

# write the label encoder to disk
with open("output/le.pickle", "wb") as f:
    pickle.dump(le, f)
