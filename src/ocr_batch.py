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
    for path in paths:
        executable_path = os.path.join(path, 'tesseract.exe')
        if os.path.isfile(executable_path):
            logging.info(f"Tesseract found at {executable_path}")
            return executable_path
    logging.error("Tesseract executable not found in any path directories.")
    return None

def preprocess_image(image_path, save_preprocessed, output_dir, threshold):
    """Pre-process the image to enhance OCR accuracy."""
    try:
        img = Image.open(image_path)
        img = img.convert('L')
        img = img.resize((img.width * 2, img.height * 2), Image.BICUBIC)
        img = img.filter(ImageFilter.MedianFilter())
        if threshold > 0:
            img = img.point(lambda p: p > threshold and 255)

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

def process_images(input_dir, language, save_preprocessed, threshold, tessdata_dir):
    """Process all images in the directory and output OCR results to a file."""
    output_file = os.path.join(input_dir, 'result.txt')
    pytesseract.pytesseract.tesseract_cmd = find_tesseract_path()
    tessdata_dir_config = r'--tessdata-dir "' + tessdata_dir + '"'

    with open(output_file, 'w', encoding='utf-8') as file_out:
        for filename in sorted([f for f in os.listdir(input_dir) if f.endswith('.jpeg') or f.endswith('.jpg')]):
            full_path = os.path.join(input_dir, filename)
            try:
                img = preprocess_image(full_path, save_preprocessed, input_dir, threshold)
                text = tesseract_ocr(img, language, tessdata_dir_config)
                file_out.write(text + '\n')
                logging.info(f"Processed {filename}")
            except Exception as e:
                logging.error(f"Failed to process {filename}: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_directory> [--language <code>] [--save-preprocessed] [--threshold <number>] [--tessdata-path <path>]")
        sys.exit(1)

    input_dir = sys.argv[1]
    language = 'eng'
    save_preprocessed = False
    threshold = 0
    tessdata_dir = ""

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--language' and i + 1 < len(sys.argv):
            language = sys.argv[i + 1]
            i += 1
        elif arg == '--save-preprocessed':
            save_preprocessed = True
        elif arg == '--threshold' and i + 1 < len(sys.argv):
            threshold = int(sys.argv[i + 1])
            i += 1
        elif arg == '--tessdata-path' and i + 1 < len(sys.argv):
            tessdata_dir = sys.argv[i + 1]
            i += 1
        i += 1

    logging.info(f"Arguments received -> Input Directory: {input_dir}, Language: {language}, Save Preprocessed: {save_preprocessed}, Threshold: {threshold}, Tessdata Directory: {tessdata_dir}")
    process_images(input_dir, language, save_preprocessed, threshold, tessdata_dir)
