import streamlit as st
import cv2
import numpy as np
import torch
import torchvision.transforms as T
import easyocr
import time
import threading

st.set_page_config(page_title="MY APP", page_icon="🚗", layout="wide")

# Load YOLOv4 weights and configuration
net = cv2.dnn.readNetFromDarknet('yolov4-obj.cfg', 'yolov4-obj_last.weights')

# Get the output layer names
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in [net.getUnconnectedOutLayers()]]

# Define the class labels
class_labels = ['license_plate']  # Add your class labels here

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])  # Specify the language(s) for license plate recognition

# Function to perform object detection
def perform_object_detection(image):
    # Convert image to blob
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)

    # Set the input to the network
    net.setInput(blob)

    # Run the forward pass
    outputs = net.forward(output_layers)

    # Get bounding box coordinates, confidence scores, and class labels
    boxes = []
    confidences = []
    class_ids = []

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:  # Adjust the confidence threshold as needed
                # Scale the bounding box coordinates to the original image size
                height, width, _ = image.shape
                box = detection[0:4] * np.array([width, height, width, height])
                (center_x, center_y, box_width, box_height) = box.astype('int')

                # Calculate the top-left corner of the bounding box
                x = int(center_x - (box_width / 2))
                y = int(center_y - (box_height / 2))

                boxes.append([x, y, int(box_width), int(box_height)])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply non-maximum suppression to remove redundant overlapping boxes
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # Draw bounding boxes and labels on the image
    #for i in range(len(boxes)):
    #    if i in indexes:
    #        x, y, w, h = boxes[i]
    #        label = class_labels[class_ids[i]]
    #        confidence = confidences[i]

    #        # Draw the bounding box and label
    #        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    #        cv2.putText(image, f'{label}: {confidence:.2f}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    #return image

    # Find license plate region and perform OCR
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = class_labels[class_ids[i]]
            confidence = confidences[i]

            if label == 'license_plate':
                # Crop license plate region
                plate_image = image[y:y+h, x:x+w]

                # Perform license plate recognition using EasyOCR
                results = reader.readtext(plate_image)

                # Extract license plate number from OCR results
                if results:
                    license_plate_number = results[0][1]
                else:
                    license_plate_number = 'No license plate number found'
                
                # Draw the bounding box and label on the original image
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image, f'{label}: {confidence:.2f}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(image, license_plate_number, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    return image

with st.container():
    st.title("License Plate Recognition")
    st.subheader("Detection Section")
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Read the image
    image = np.array(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    # Perform object detection and license plate recognition
    output_image = perform_object_detection(image)

    # Display the output image
    st.image(output_image, channels="BGR")