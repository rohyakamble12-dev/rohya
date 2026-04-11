import cv2
import os

class VisionSensor:
    @staticmethod
    def analyze_scene():
        """Captures a frame from the webcam and performs basic face detection."""
        try:
            # Attempt to open the default camera
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return "I'm unable to access the optical sensor."

            ret, frame = cap.read()
            if not ret:
                cap.release()
                return "I couldn't capture a clear image from the sensor."

            # Load the pre-trained Haar Cascade for face detection
            # Make sure we find the default haarcascade file
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)

            # Convert frame to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            num_faces = len(faces)

            # Cleanup
            cap.release()

            if num_faces == 0:
                return "Optical sensor is active. I don't see anyone in the immediate vicinity."
            elif num_faces == 1:
                return "Optical sensor is active. I see one person in my view."
            else:
                return f"Optical sensor is active. I see {num_faces} people in my view."

        except Exception as e:
            return f"An error occurred while accessing the optical sensor: {str(e)}"
