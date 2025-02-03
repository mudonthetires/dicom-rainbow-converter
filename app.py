from flask import Flask, request, render_template, send_from_directory, jsonify
import os
import cv2
import numpy as np
import pydicom
from PIL import Image

app = Flask(__name__)

# Ensure directories exist
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    filepath = os.path.join(UPLOAD_FOLDER, 'input.dcm')
    file.save(filepath)

    # Ensure file exists after saving
    if not os.path.exists(filepath):
        return "DICOM file not found after upload", 500

    try:
        # Process and convert DICOM to PNG/JPG
        ds = pydicom.dcmread(filepath)
        img_array = ds.pixel_array.astype(np.uint8)  # Ensure correct data type

        # Normalize to 8-bit
        img_array = ((img_array - img_array.min()) / (img_array.max() - img_array.min()) * 255).astype(np.uint8)

        # Convert to RGB
        img = Image.fromarray(img_array).convert("RGB")
        processed_filename = "processed_image.jpg"
        processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)
        img.save(processed_path)

        return render_template('result.html', filename=processed_filename)
    
    except Exception as e:
        return f"Error processing DICOM file: {str(e)}", 500

@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename, as_attachment=True)

@app.route('/crop_image', methods=['POST'])
def crop_image():
    try:
        data = request.json
        x, y, w, h = data['x'], data['y'], data['width'], data['height']
        window, level = int(data['window']), int(data['level'])

        dicom_path = os.path.join(UPLOAD_FOLDER, 'input.dcm')
        if not os.path.exists(dicom_path):
            return jsonify({"error": "DICOM file not found"}), 500

        ds = pydicom.dcmread(dicom_path)
        img_array = ds.pixel_array.astype(np.uint8)

        # Apply windowing
        img_array = np.clip(img_array + window, 0, 255)

        # Crop the image
        cropped_img = img_array[y:y+h, x:x+w]

        # Convert to RGB and save
        img = Image.fromarray(cropped_img).convert("RGB")
        cropped_filename = "cropped_output.jpg"
        cropped_path = os.path.join(PROCESSED_FOLDER, cropped_filename)
        img.save(cropped_path)

        return jsonify({"filename": cropped_filename})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
