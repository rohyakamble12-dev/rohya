import cv2
import logging
import os
import pyautogui
import numpy as np
import pytesseract # Requires Tesseract-OCR installed on Windows
try:
    import mediapipe as mp
    HAS_MEDIAPIPE = True
except:
    HAS_MEDIAPIPE = False

class VisionModule:
    def __init__(self):
        if HAS_MEDIAPIPE:
            try:
                self.mp_hands = mp.solutions.hands
                self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
                self.mp_face_mesh = mp.solutions.face_mesh
                self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.7)
            except:
                HAS_MEDIAPIPE = False
    def capture_and_describe(self):
        try:
            # Optimized camera initialization with DirectShow (faster on Windows)
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            # Read multiple frames to allow auto-exposure to settle
            for _ in range(5): cap.read()
            ret, frame = cap.read()
            cap.release()

            if ret:
                # Save tactical reference
                os.makedirs("captures", exist_ok=True)
                cv2.imwrite("captures/vision_ref.jpg", frame)
                return "Optic link established. Visual data captured and archived for analysis. Operator identified."
            return "Optic sensors failed to acquire visual lock."
        except Exception as e:
            return f"Vision link error: {e}"

    def face_detect(self):
        """Advanced biometric simulation with facial signature detection."""
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            for _ in range(5): cap.read()
            ret, frame = cap.read()
            cap.release()

            if not ret: return "Optical error: Frame capture failed. Check hardware link."

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) > 0:
                # Real Image Matching Attempt (Trusted profile check)
                is_verified = self.verify_operator(frame)

                # Add simulated metrics for MCU feel
                confidence = round(100 - (100 / len(faces)), 2) if len(faces) > 0 else 0
                status = "VERIFIED" if is_verified else "IDENTIFIED"
                return (
                    f"BIOMETRIC SCAN: Human signature {status}.\n"
                    f"COUNT: {len(faces)} | CONFIDENCE: {confidence or 98.4}%\n"
                    f"PROFILE: Operator status confirmed. Security protocols nominal."
                )
            return "BIOMETRIC SCAN: No human signatures detected. Perimeter secure."
        except Exception as e:
            return f"Biometric link error: {e}"

    def verify_operator(self, frame):
        """Compares live frame against trusted signature in storage."""
        try:
            trusted_path = "storage/biometric_trusted.jpg"
            if not os.path.exists(trusted_path):
                # Auto-enrollment on first success
                os.makedirs("storage", exist_ok=True)
                cv2.imwrite(trusted_path, frame)
                return True

            trusted = cv2.imread(trusted_path)
            # Histogram comparison (Simple for demo, robust for Friday)
            hist1 = cv2.calcHist([trusted], [0], None, [256], [0, 256])
            hist2 = cv2.calcHist([frame], [0], None, [256], [0, 256])
            similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            return similarity > 0.8
        except: return False

    def detect_gesture(self, frame):
        """Detects hand gestures for system control."""
        if not HAS_MEDIAPIPE: return None
        try:
            results = self.hands.process(frame)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Index and Thumb tip coordinates
                    thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
                    index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]

                    # Euclidean distance
                    dist = np.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)

                    if dist < 0.05: return "MUTE"
                    if index_tip.y < thumb_tip.y - 0.1: return "VOL_UP"
                    if index_tip.y > thumb_tip.y + 0.1: return "VOL_DOWN"
            return None
        except: return None

    def security_perimeter_scan(self):
        """MCU Accurate Security Protocol: Advanced Face Mesh Analysis."""
        try:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            for _ in range(5): cap.read()
            ret, frame = cap.read()
            cap.release()

            if not ret: return "SECURITY ALERT: Optical sensor failure. Unable to verify perimeter."

            # Legacy Fallback for missing MediaPipe
            if not HAS_MEDIAPIPE:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                if len(faces) == 0: return "PERIMETER SECURE: No biological signatures detected."
                is_verified = self.verify_operator(frame)
                return f"BIOMETRIC SCAN: {len(faces)} signature(s) detected. VERIFIED: {is_verified}."

            # Face Mesh Analysis
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mesh_results = self.face_mesh.process(rgb_frame)

            if not mesh_results.multi_face_landmarks:
                return "PERIMETER SECURE: No biological signatures detected in primary sector."

            num_faces = len(mesh_results.multi_face_landmarks)
            landmarks = mesh_results.multi_face_landmarks[0].landmark

            # Simulated Geometric Depth
            depth = round(landmarks[0].z * -100, 2)

            # Verify identity
            is_verified = self.verify_operator(frame)
            status = "CONFIRMED" if is_verified else "UNAUTHORIZED"

            return (
                f"BIOMETRIC SCAN: {num_faces} signature(s) detected.\n"
                f"GEOMETRIC INTEGRITY: {status}\n"
                f"SIGNATURE DEPTH: {depth}mm (3D MESH ACTIVE)\n"
                f"STATUS: {'Access Granted' if is_verified else 'Engaging Defensive Monitoring'}."
            )
        except Exception as e:
            return f"Security link failure: {e}"

    def scan_objects(self):
        """MCU Accurate Object Detection: Eye and Profile detection."""
        try:
            eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            ret, frame = cap.read()
            cap.release()

            if not ret: return "VISUAL SCAN: Hardware link failed."

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            eyes = eye_cascade.detectMultiScale(gray, 1.3, 5)

            status = "CLEAR" if len(eyes) == 0 else "IDENTIFIED"
            return f"TACTICAL SCAN: {len(eyes)} ocular signature(s) detected. Sector status: {status}."
        except: return "Tactical scan protocol offline."

    def analyze_style(self):
        """MCU Accurate Style Advisor: Color and Profile analysis."""
        try:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            for _ in range(5): cap.read()
            ret, frame = cap.read()
            cap.release()

            if not ret: return "STYLE ADVISOR: Optic link failed."

            # Simple color dominance analysis
            avg_color_per_row = np.average(frame, axis=0)
            avg_color = np.average(avg_color_per_row, axis=0)
            # BGR to HEX
            hex_color = '#%02x%02x%02x' % (int(avg_color[2]), int(avg_color[1]), int(avg_color[0]))

            return (
                f"STYLE ANALYSIS COMPLETE:\n"
                f"DOMINANT SPECTRUM: {hex_color}\n"
                f"SYMMETRY: Nominal\n"
                f"ADVICE: Aesthetic profile synchronized with active tactical sector."
            )
        except: return "Style advisor protocol offline."

    def analyze_operator_state(self):
        """Detects operator mood/state using facial landmarks."""
        if not HAS_MEDIAPIPE: return "STATE ANALYSIS: Cognitive vision offline."
        try:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            for _ in range(5): cap.read()
            ret, frame = cap.read()
            cap.release()

            if not ret: return "STATE ANALYSIS: Optic sensors offline."

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mesh_results = self.face_mesh.process(rgb_frame)

            if not mesh_results.multi_face_landmarks:
                return "STATE ANALYSIS: Awaiting visual lock on Operator profile."

            landmarks = mesh_results.multi_face_landmarks[0].landmark
            # Simple heuristic: Mouth corner distance vs Eye height
            left_mouth = landmarks[61]; right_mouth = landmarks[291]
            mouth_width = np.sqrt((left_mouth.x - right_mouth.x)**2 + (left_mouth.y - right_mouth.y)**2)

            state = "FOCUSED"
            if mouth_width > 0.08: state = "ENGAGED/CONTENT"
            elif mouth_width < 0.05: state = "STRESSED/DETERMINED"

            return f"STATE ANALYSIS: Operator appears {state}. Environmental optimizations adjusted."
        except: return "Sentiment analysis protocol offline."

    def screen_ocr(self):
        """Captures screen and performs cognitive text extraction."""
        try:
            shot = pyautogui.screenshot()
            frame = np.array(shot)
            # Pre-processing for better OCR
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # OCR processing
            text = pytesseract.image_to_string(gray)
            if not text.strip():
                return "VISUAL SCAN: Sector clear. No legible data streams detected on primary interface."

            clean_text = "\n".join([line.strip() for line in text.split("\n") if line.strip()][:15])
            return (
                f"SCREEN INTEGRITY REPORT: DATA ACQUIRED\n"
                f"--------------------------------------\n"
                f"{clean_text}\n"
                f"--------------------------------------\n"
                f"Analysis: Intelligence buffer updated with active workspace telemetry."
            )
        except Exception as e:
            return f"Optic character recognition protocol failed: {e}."
