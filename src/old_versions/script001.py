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
    tesseract_cmd = None
    # Define the pattern to search for the executable
    pattern = re.compile(r'tesseract-ocr\\tesseract.exe$', re.IGNORECASE)
    for path in paths:
        executable_path = os.path.join(path, 'tesseract.exe')
        if os.path.isfile(executable_path):
            tesseract_cmd = executable_path
            break
    if tesseract_cmd:
        logging.info(f"Tesseract found at {tesseract_cmd}")
    else:
        logging.error("Tesseract executable not found in any path directories.")
    return tesseract_cmd

def preprocess_image(image_path, save_preprocessed, output_dir):
    """Pre-process the image to enhance OCR accuracy."""
    try:
        img = Image.open(image_path)
        img = ImageOps.exif_transpose(img)  # Correct orientation based on EXIF data
        img = img.convert('L')  # Convert to grayscale
        img = img.resize((img.width * 2, img.height * 2), Image.BICUBIC)  # Scale image

        # Apply adaptive thresholding
        img = img.point(lambda x: 0 if x < 128 else 255, '1')

        if save_preprocessed:
            preprocessed_path = os.path.join(output_dir, 'preprocessed_images')
            if not os.path.exists(preprocessed_path):
                os.makedirs(preprocessed_path)
            preprocessed_image_path = os.path.join(preprocessed_path, os.path.basename(image_path))
            img.save(preprocessed_image_path)
            logging.info(f"Saved preprocessed image to {preprocessed_image_path}")

        return img
    except Exception as e:
        logging.exception("Failed to preprocess image.")
        raise RuntimeError("Failed to preprocess image") from e

def tesseract_ocr(image, language, tessdata_dir_config):
    """Run OCR on the processed image with specified language."""
    try:
        custom_config = r'--oem 3 --psm 3 -l ' + language + ' ' + tessdata_dir_config
        text = pytesseract.image_to_string(image, config=custom_config)
        return text
    except Exception as e:
        logging.exception("OCR failed.")
        raise RuntimeError("OCR failed") from e

def process_images(input_dir, output_file, language, save_preprocessed, tesseract_cmd, tessdata_dir):
    """Process all images in the directory and output OCR results to a file."""
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    tessdata_dir_config = r'--tessdata-dir "' + tessdata_dir + '"'

    with open(output_file, 'w', encoding='utf-8') as file_out:
        for filename in sorted([f for f in os.listdir(input_dir) if f.endswith('.jpeg') or f.endswith('.jpg')]):
            full_path = os.path.join(input_dir, filename)
            try:
                img = preprocess_image(full_path, save_preprocessed, input_dir)
                text = tesseract_ocr(img, language, tessdata_dir_config)
                file_out.write(text + '\n')
                logging.info(f"Processed {filename}")
            except Exception as e:
                logging.error(f"Failed to process {filename}: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        logging.error("Usage: python batch_ocr.py <input_directory> <output_file> [language_code] [--save-preprocessed] [--tesseract-path <path_to_tesseract>] [--tessdata-path <path_to_tessdata>]")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_file = sys.argv[2]
    language = 'deu'  # Default language
    save_preprocessed = False
    tesseract_cmd = find_tesseract_path() if '--tesseract-path' not in sys.argv else None
    tessdata_dir = ""

    i = 3
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--save-preprocessed':
            save_preprocessed = True
        elif arg == '--tesseract-path' and i + 1 < len(sys.argv):
            tesseract_cmd = sys.argv[i + 1]
            i += 1
        elif arg == '--tessdata-path' and i + 1 < len(sys.argv):
            tessdata_dir = sys.argv[i + 1]
            i += 1
        elif len(arg) == 3 and arg.isalpha():
            language = arg
        i += 1

    process_images(input_dir, output_file, language, save_preprocessed, tesseract_cmd, tessdata_dir)
