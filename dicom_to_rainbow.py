import pydicom
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from PIL import Image

def convert_dicom_to_rainbow(dicom_file_path, output_file_path):
    # Read the DICOM file
    dicom_data = pydicom.dcmread(dicom_file_path)

    # Extract the pixel data
    pixel_array = dicom_data.pixel_array

    # Normalize the pixel array to the range [0, 1] for applying the color map
    norm = Normalize(vmin=np.min(pixel_array), vmax=np.max(pixel_array))
    rainbow_image = plt.cm.rainbow(norm(pixel_array))

    # Convert to 8-bit RGB (0-255) for saving as JPEG
    rainbow_image = (rainbow_image[:, :, :3] * 255).astype(np.uint8)

    # Save the image as a JPEG file using PIL
    image = Image.fromarray(rainbow_image)
    image.save(output_file_path, format="JPEG")
    
    print(f"Rainbow DICOM image saved to {output_file_path}")

# Example usage
convert_dicom_to_rainbow('input.dcm', 'output_rainbow.jpg')
