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
    pattern = re.compile(r'tesseract\.exe$', re.IGNORECASE)
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
        img = img.convert('L')  # Convert to grayscale
        img = img.resize((img.width * 2, img.height * 2), Image.BICUBIC)  # Scale image
        img = img.filter(ImageFilter.MedianFilter())  # Apply median filter to remove noise
        if threshold > 0:
            img = img.point(lambda p: p > threshold and 255)

        if save_preprocessed:
            preprocessed_path = os.path.join(output_dir, 'preprocessed_images')
            os.makedirs(preprocessed_path, exist_ok=True)
            preprocessed_image_path = os.path.join(preprocessed_path, os.path.basename(image_path))
            img.save(preprocessed_image_path)
            logging.info(f"Saved preprocessed image to {preprocessed_image_path}")

        return img
    except Exception as e:
        logging.exception("Failed to preprocess image.")
        raise RuntimeError("Failed to preprocess image") from e

def tesseract_ocr(image, language, tessdata_dir_config, tesseract_cmd):
    """Run OCR on the processed image with specified language."""
    if tesseract_cmd is None:
        raise RuntimeError("Tesseract executable not found.")
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    config = f'--oem 3 --psm 3 -l {language} {tessdata_dir_config}'
    return pytesseract.image_to_string(image, config=config)

def process_images(input_dir, language, save_preprocessed, threshold, tessdata_dir):
    """Process all images in the directory and output OCR results to a file."""
    output_file = os.path.join(input_dir, "result.txt")
    tessdata_dir_config = f'--tessdata-dir "{tessdata_dir}"'
    tesseract_cmd = find_tesseract_path()
    if not tesseract_cmd:
        logging.error("Tesseract path not found. Please ensure Tesseract is installed and in your PATH.")
        return

    with open(output_file, 'w', encoding='utf-8') as file_out:
        for filename in sorted(os.listdir(input_dir)):
            if filename.lower().endswith(('.jpeg', '.jpg', '.png')):
                full_path = os.path.join(input_dir, filename)
                img = preprocess_image(full_path, save_preprocessed, input_dir, threshold)
                text = tesseract_ocr(img, language, tessdata_dir_config, tesseract_cmd)
                file_out.write(text + '\n')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        logging.error("Insufficient arguments provided.")
        print("Usage: python script.py <input_directory> [language_code] [--save-preprocessed] [threshold] [--tessdata-path <path_to_tessdata>]")
        sys.exit(1)

    input_dir = sys.argv[1]
    language = 'eng'  # Default language
    save_preprocessed = False
    threshold = 0
    tessdata_dir = ""

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--save-preprocessed':
            save_preprocessed = True
        elif arg.isdigit():
            threshold = int(arg)
        elif arg == '--tessdata-path' and i + 1 < len(sys.argv):
            tessdata_dir = sys.argv[i + 1]
            i += 1
        elif len(arg) == 3 and arg.isalpha():
            language = arg
        i += 1

    process_images(input_dir, language, save_preprocessed, threshold, tessdata_dir)
