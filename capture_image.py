import cv2
import os
import time

def create_user_dataset(username, num_images=20):
    # Create directory for the user if it doesn't exist
    dataset_path = os.path.join("dataset", username)
    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path)

    # Start video capture (webcam)
    cap = cv2.VideoCapture(0)

    # Set properties to improve image quality
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    # Initialize counter for the number of images captured
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

if __name__ == "__main__":
    # Get username input
    username = input("Enter your username: ")
    if username:
        create_user_dataset(username)
    else:
        print("[ERROR] Username cannot be empty.")
