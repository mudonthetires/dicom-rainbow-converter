import os
import pydicom
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from PIL import Image
from flask import Flask, request, render_template, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def convert_dicom_to_rainbow(dicom_file_path, output_file_path):
    """Converts a DICOM grayscale image to a rainbow-colored JPEG."""
    try:
        dicom_data = pydicom.dcmread(dicom_file_path)
        pixel_array = dicom_data.pixel_array

        norm = Normalize(vmin=np.min(pixel_array), vmax=np.max(pixel_array))
        rainbow_image = plt.cm.rainbow(norm(pixel_array))

        # Convert to 8-bit RGB
        rainbow_image = (rainbow_image[:, :, :3] * 255).astype(np.uint8)

        # Save as JPEG
        image = Image.fromarray(rainbow_image)
        image.save(output_file_path, format="JPEG")

        return True
    except Exception as e:
        print(f"Error processing DICOM file: {e}")
        return False

@app.route("/", methods=["GET", "POST"])
def upload_file():
    """Handles DICOM file upload, processing, and displaying the result."""
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"

        file = request.files["file"]
        if file.filename == "":
            return "No selected file"

        if file:
            dicom_path = os.path.join(UPLOAD_FOLDER, file.filename)
            output_filename = file.filename.replace(".dcm", ".jpg")
            output_path = os.path.join(PROCESSED_FOLDER, output_filename)

            file.save(dicom_path)

            if convert_dicom_to_rainbow(dicom_path, output_path):
                return render_template("result.html", filename=output_filename)
            else:
                return "Error processing file"

    return render_template("upload.html")

@app.route("/processed/<filename>")
def processed_file(filename):
    """Displays the processed image."""
    return send_from_directory(PROCESSED_FOLDER, filename)

@app.route("/download/<filename>")
def download_file(filename):
    """Provides a download link for the processed image."""
    return send_from_directory(PROCESSED_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    
	port = int(os.environ.get("PORT", 5000))  # Use Render's provided port
    
	app.run(host="0.0.0.0", port=port, debug=False)