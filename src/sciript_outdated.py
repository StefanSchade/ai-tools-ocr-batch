import sys
import os
import re
import logging
from PIL import Image, ImageFilter, ImageOps
import pytesseract
import json

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


def tesseract_ocr(image, language, tessdata_dir_config, tesseract_cmd):
    """Run OCR on the processed image with specified language and return text with confidence score."""
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    custom_config = f'--oem 3 --psm 3 -l {language} {tessdata_dir_config}'
    data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
    text = ' '.join([data['text'][i] for i in range(len(data['text'])) if int(data['conf'][i]) > 60])
    average_confidence = sum([int(c) for c in data['conf'] if c.isdigit()]) / len(
        [c for c in data['conf'] if c.isdigit()]) if data['conf'] else 0
    return text, average_confidence


def process_images(input_dir, output_file, language, save_preprocessed, threshold, tesseract_cmd, tessdata_dir):
    """Process all images in the directory and output OCR results to a file with confidence metadata."""
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    tessdata_dir_config = f'--tessdata-dir "{tessdata_dir}"'

    with open(output_file, 'w', encoding='utf-8') as file_out:
        for index, filename in enumerate(
                sorted([f for f in os.listdir(input_dir) if f.endswith('.jpeg') or f.endswith('.jpg')])):
            full_path = os.path.join(input_dir, filename)
            try:
                img = preprocess_image(full_path, save_preprocessed, input_dir, threshold)
                text, confidence = tesseract_ocr(img, language, tessdata_dir_config, tesseract_cmd)
                # Write JSON header for the page
                page_info = {
                    "new_page": True,
                    "page_number": index + 1,
                    "page_file": filename,
                    "average_confidence": confidence
                }
                file_out.write(json.dumps(page_info) + '\n')
                file_out.write(text + '\n')
                logging.info(f"Processed {filename} with average confidence: {confidence}")
            except Exception as e:
                logging.error(f"Failed to process {filename}: {e}")


# Initial setup as before
def main():
    if len(sys.argv) < 2:
        print("Usage: python sciript_outdated.py <input_directory> [--language <lang_code>] [--save-preprocessed] [--threshold <int>] [--tessdata-path <path_to_tessdata>] [--check-orientation]")
        sys.exit(1)

    input_dir = sys.argv[1]
    language = 'deu'  # Default to German; override if specified
    save_preprocessed = False
    threshold = 0
    tessdata_dir = ""
    check_orientation = False

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--language' and i + 1 < len(sys.argv):
            language = sys.argv[i + 1]
            i += 1
        elif sys.argv[i] == '--save-preprocessed':
            save_preprocessed = True
        elif sys.argv[i] == '--threshold' and i + 1 < len(sys.argv):
            threshold = int(sys.argv[i + 1])  # Convert string to integer here
            i += 1
        elif sys.argv[i] == '--tessdata-path' and i + 1 < len(sys.argv):
            tessdata_dir = sys.argv[i + 1]
            i += 1
        elif sys.argv[i] == '--check-orientation':
            check_orientation = True
        i += 1

    tesseract_cmd = find_tesseract_path()
    if not tessdata_dir:  # If tessdata path not specifically provided
        tessdata_dir = os.path.join(os.path.dirname(tesseract_cmd), 'tessdata') if tesseract_cmd else ""

    # Print configuration for debugging
    logging.info(f"Arguments received -> Input Directory: {input_dir}, Language: {language}, Save Preprocessed: {save_preprocessed}, Threshold: {threshold}, Tessdata Directory: {tessdata_dir}, Check Orientation: {check_orientation}")

    # Call the function with all required parameters
    process_images(input_dir, language, save_preprocessed, threshold, tesseract_cmd, tessdata_dir, check_orientation)

if __name__ == '__main__':
    main()