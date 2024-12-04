import tensorflow as tf
import numpy as np
import cv2
import logging

class CustomClassifier:
    def __init__(self, model_path, labels_path, custom_objects=None):
        try:
            self.model = tf.keras.models.load_model(model_path, compile=False, custom_objects=custom_objects)
            logging.info("Model loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading model: {e}")
            raise e

        try:
            with open(labels_path, 'r') as f:
                self.labels = f.read().splitlines()
            logging.info("Labels loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading labels: {e}")
            raise e

    def getPrediction(self, img):
        try:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            img = img / 255.0

            img = np.expand_dims(img, axis=0)

            predictions = self.model.predict(img)

            index = np.argmax(predictions)

            confidence = predictions[0][index]

            label = self.labels[index] if index < len(self.labels) else "Unknown"

            return confidence, index, label
        except Exception as e:
            logging.error(f"Error during prediction: {e}")
            return None, None, None
