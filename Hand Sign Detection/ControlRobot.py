import cv2
from cvzone.HandTrackingModule import HandDetector
from CustomClassifier import CustomClassifier
import numpy as np
import math
import logging
import socketz
from CustomLayers import FixedDepthwiseConv2D

logging.basicConfig(level=logging.INFO)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 5005)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    logging.error("Error: Could not open webcam.")
    exit()

detector = HandDetector(maxHands=1)

try:
    classifier = CustomClassifier(
        "Model/keras_model.h5",
        "Model/labels.txt",
        custom_objects={'DepthwiseConv2D': FixedDepthwiseConv2D}
    )
    logging.info("Classifier initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize classifier: {e}")
    exit()

offset = 20
imgSize = 224

gesture_to_command = {
    "FORWARD": "FORWARD",
    "REVERSE": "REVERSE",
    "LEFT": "LEFT",
    "RIGHT": "RIGHT",
    "STOP": "STOP"
}

while True:
    success, img = cap.read()
    imgOutput = img.copy()
    if not success:
        logging.warning("Failed to grab frame.")
        break

    hands, img = detector.findHands(img)
    gesture_label = "No gesture"

    if hands:
        hand = hands[0]
        if 'bbox' in hand:
            x, y, w, h = hand['bbox']

            height, width, _ = img.shape

            x1 = max(x - offset, 0)
            y1 = max(y - offset, 0)
            x2 = min(x + w + offset, width)
            y2 = min(y + h + offset, height)

            imgCrop = img[y1:y2, x1:x2]

            if imgCrop.size == 0:
                logging.warning("Cropped image is empty.")
                continue

            imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255

            aspectRatio = h / w if w != 0 else 1

            if aspectRatio > 1:
                k = imgSize / h
                wCal = math.ceil(k * w)
                imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                wGap = math.ceil((imgSize - wCal) / 2)
                imgWhite[:, wGap:wCal + wGap] = imgResize
            else:
                k = imgSize / w
                hCal = math.ceil(k * h)
                imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                hGap = math.ceil((imgSize - hCal) / 2)
                imgWhite[hGap:hCal + hGap, :] = imgResize

            try:
                confidence, index, label = classifier.getPrediction(imgWhite)
                if label:
                    gesture_label = f"{label} ({confidence * 100:.2f}%)"
                    logging.info(f"Prediction: {gesture_label}")

                    command = gesture_to_command.get(label, "STOP")
                    logging.info(f"Sending command: {command}")
                    server_socket.sendto(command.encode(), server_address)


            except Exception as e:
                logging.error(f"Error during prediction: {e}")

    cv2.putText(img, gesture_label, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

    cv2.imshow("Image", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        logging.info("Exiting...")
        break

cap.release()
cv2.destroyAllWindows()
