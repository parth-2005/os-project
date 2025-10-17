"""OCR (Optical Character Recognition) processing module"""
import base64
import json
from PIL import Image
import pytesseract

def process_ocr(image_files):
    """
    Perform OCR on image files to extract text content.
    Returns extracted text and metadata for each image.
    """
    results = []
    for image_file in image_files:
        try:
            # Open image
            img = Image.open(image_file.stream)
            
            # Perform OCR
            extracted_text = pytesseract.image_to_string(img)
            
            # Get additional data
            ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            
            # Calculate confidence scores
            confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            ocr_result = {
                "extracted_text": extracted_text,
                "word_count": len(extracted_text.split()),
                "character_count": len(extracted_text),
                "average_confidence": avg_confidence,
                "image_size": img.size,
                "image_mode": img.mode
            }
            
            # Encode as base64 JSON
            result_str = base64.b64encode(json.dumps(ocr_result).encode()).decode('utf-8')
            
            results.append({
                "filename": image_file.filename,
                "ocr_data": result_str
            })
        except Exception as e:
            print(f"Error processing OCR for {image_file.filename}: {e}")
    
    return results