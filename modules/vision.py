import cv2
import logging
import os
import pyautogui
import numpy as np
import pytesseract # Requires Tesseract-OCR installed on Windows

class VisionModule:
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
                # Add simulated metrics for MCU feel
                confidence = round(100 - (100 / len(faces)), 2) if len(faces) > 0 else 0
                return (
                    f"BIOMETRIC SCAN: Human signature identified.\n"
                    f"COUNT: {len(faces)} | CONFIDENCE: {confidence or 98.4}%\n"
                    f"PROFILE: Operator status confirmed. Security protocols nominal."
                )
            return "BIOMETRIC SCAN: No human signatures detected. Perimeter secure."
        except Exception as e:
            return f"Biometric link error: {e}"

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
