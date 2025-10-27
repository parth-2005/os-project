import io
import base64
from PIL import Image

def process_images(image_files):
    """Process list of Werkzeug FileStorage objects and return list of results with filename and base64 image data."""
    results = []
    for image in image_files:
        try:
            img = Image.open(image.stream)
            grayscale_img = img.convert("L")
            buffered = io.BytesIO()
            grayscale_img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            results.append({
                "filename": image.filename,
                "image_data": img_str
            })
        except Exception as e:
            print(f"Error processing image {image.filename}: {e}")
    return results
