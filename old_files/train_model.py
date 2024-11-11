# import the necessary packages
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import pickle
import os

# create output directory if it doesn't exist
if not os.path.exists("output"):
    os.makedirs("output")

# load the face embeddings
embeddings_path = "output/embeddings.pickle"
print(f"[INFO] loading face embeddings from {embeddings_path}...")
with open(embeddings_path, "rb") as f:
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
recognizer_path = "output/recognizer.pickle"
print(f"[INFO] saving recognizer model to {recognizer_path}...")
with open(recognizer_path, "wb") as f:
    pickle.dump(recognizer, f)

# write the label encoder to disk
le_path = "output/le.pickle"
print(f"[INFO] saving label encoder to {le_path}...")
with open(le_path, "wb") as f:
    pickle.dump(le, f)

print("[INFO] Model training complete.")
