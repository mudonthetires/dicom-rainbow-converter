import os
import cv2
import numpy as np
import pydicom
from flask import Flask, request, render_template, send_from_directory
from PIL import Image

app = Flask(__name__)

# Ensure required directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('processed', exist_ok=True)

# Function to convert DICOM to a rainbow image
def dicom_to_rainbow(dicom_path, output_path, window_center=40, window_width=80):
    dicom_data = pydicom.dcmread(dicom_path)
    pixel_array = dicom_data.pixel_array.astype(np.float32)

    # Apply windowing (adjust contrast & brightness)
    min_val = window_center - (window_width / 2)
    max_val = window_center + (window_width / 2)
    pixel_array = np.clip(pixel_array, min_val, max_val)

    # Normalize to 0-255 range
    pixel_array = ((pixel_array - min_val) / (max_val - min_val) * 255).astype(np.uint8)

    # Apply a rainbow colormap
    rainbow_image = cv2.applyColorMap(pixel_array, cv2.COLORMAP_JET)

    # Convert to RGB and save as JPEG
    rgb_image = cv2.cvtColor(rainbow_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)
    pil_image.save(output_path, format="JPEG")

# Route for file upload
@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file uploaded!", 400

        file = request.files["file"]
        if file.filename == "":
            return "No selected file!", 400

        # Save uploaded DICOM file
        dicom_path = os.path.join("uploads", file.filename)
        file.save(dicom_path)

        # Process DICOM file
        output_filename = file.filename.replace(".dcm", ".jpg")
        output_path = os.path.join("processed", output_filename)
        dicom_to_rainbow(dicom_path, output_path)

        return render_template("result.html", filename=output_filename)

    return render_template("upload.html")

# Route to serve processed images
@app.route("/processed/<filename>")
def processed_file(filename):
    return send_from_directory("processed", filename)

# Route to download processed images
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory("processed", filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
