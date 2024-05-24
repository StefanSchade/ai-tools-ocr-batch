import sys
import os
import re
import logging
from PIL import Image, ImageFilter, ImageOps
import pytesseract

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def find_tesseract_path():
    """Find the Tesseract executable in the system PATH."""
    paths = os.getenv('PATH').split(os.pathsep)
    pattern = re.compile(r'tesseract-ocr\\tesseract.exe$', re.IGNORECASE)
    for path in paths:
        executable_path = os.path.join(path, 'tesseract.exe')
        if os.path.isfile(executable_path):
            logging.info(f"Tesseract found at {executable_path}")
            return executable_path
    logging.error("Tesseract executable not found in any path directories.")
    return None

def preprocess_image(image_path):
    """Pre-process the image to enhance OCR accuracy."""
    try:
        img = Image.open(image_path)
        img = img.convert('L')  # Convert to grayscale
        img = img.resize((img.width * 2, img.height * 2), Image.BICUBIC)  # Scale image
        img = img.filter(ImageFilter.MedianFilter())  # Apply median filter to remove noise
        return img
    except Exception as e:
        logging.exception("Failed to preprocess image.")
        raise RuntimeError("Failed to preprocess image") from e

def get_ocr_data(img, language='eng'):
    """Extract detailed OCR data including confidence scores."""
    data = pytesseract.image_to_data(img, lang=language, output_type=pytesseract.Output.DICT)
    return data

def best_orientation(img, language):
    """Determine the best orientation for OCR by testing multiple rotations."""
    orientations = [0, 90, 180, 270]
    best_confidence = 0
    best_text = ""
    best_orientation = 0

    for angle in orientations:
        rotated_img = img.rotate(angle, expand=True)
        data = get_ocr_data(rotated_img, language)
        confidences = [int(conf) for conf, text in zip(data['conf'], data['text']) if text.strip() and int(conf) > 0]
        average_confidence = sum(confidences) / len(confidences) if confidences else 0

        if average_confidence > best_confidence:
            best_confidence = average_confidence
            best_orientation = angle
            best_text = ' '.join([data['text'][i] for i in range(len(data['text'])) if int(data['conf'][i]) > 0])

    return best_orientation, best_text

def process_images(input_dir, output_file, language, check_orientation):
    """Process all images in the directory and output OCR results to a file."""
    tesseract_cmd = find_tesseract_path()
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    with open(output_file, 'w', encoding='utf-8') as file_out:
        for filename in sorted(os.listdir(input_dir)):
            if filename.lower().endswith(('.jpeg', '.jpg', '.png')):
                full_path = os.path.join(input_dir, filename)
                try:
                    img = preprocess_image(full_path)
                    if check_orientation:
                        angle, text = best_orientation(img, language)
                        logging.info(f"Best orientation for {filename} is {angle} degrees.")
                    else:
                        text = pytesseract.image_to_string(img, lang=language)
                    file_out.write(text + '\n')
                    logging.info(f"Processed {filename}")
                except Exception as e:
                    logging.error(f"Failed to process {filename}: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        logging.error("Usage: python batch_ocr.py <input_directory> <output_file> [language] [--check-orientation]")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_file = sys.argv[2]
    language = sys.argv[3] if len(sys.argv) > 3 else 'eng'
    check_orientation = '--check-orientation' in sys.argv

    process_images(input_dir, output_file, language, check_orientation)
