import sys
import os
import re
import logging
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import pytesseract
import json

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants for the rotation check algorithm
HIGH_CONFIDENCE_THRESHOLD = 40
SMALL_ROTATION_STEP = 1
MAX_ROTATION_STEPS = 10

def find_tesseract_path():
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
    img = Image.open(image_path)
    img = img.convert('L')
    img = img.resize((img.width * 2, img.height * 2), Image.BICUBIC)
    img = img.filter(ImageFilter.MedianFilter())
    if threshold > 0:
        img = img.point(lambda p: p > threshold and 255)
    return img

def check_orientations(image, language, tessdata_dir_config, tesseract_cmd, check_orientation):
    orientations = [0, 90, 180, 270]
    best_text = ''
    highest_confidence = -1
    final_angle = 0

    for angle in orientations:
        rotated_image = image.rotate(angle, expand=True)
        text, confidence = tesseract_ocr(rotated_image, language, tessdata_dir_config, tesseract_cmd)
        if confidence > highest_confidence:
            highest_confidence = confidence
            best_text = text
            final_angle = angle
            if confidence > HIGH_CONFIDENCE_THRESHOLD:
                break

    if check_orientation == 2: # perform fine grained optimization
        for step in range(MAX_ROTATION_STEPS):
            adjustments = [SMALL_ROTATION_STEP, -SMALL_ROTATION_STEP]
            for adjustment in adjustments:
                logging.debug(f"Adjusting angle: {final_angle + adjustment}")
                adjusted_image = image.rotate(final_angle + adjustment, expand=True)
                adjusted_text, adjusted_confidence = tesseract_ocr(adjusted_image, language, tessdata_dir_config, tesseract_cmd)
                if adjusted_confidence > highest_confidence:
                    highest_confidence = adjusted_confidence
                    final_angle += adjustment
                    best_text = adjusted_text
                    break

    return best_text, final_angle, confidence

def tesseract_ocr(image, language, tessdata_dir_config, tesseract_cmd):
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    config = f'--oem 3 --psm 3 -l {language} {tessdata_dir_config}'
    data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
    text = ' '.join([data['text'][i] for i in range(len(data['text'])) if data['conf'][i] > 60])
    average_confidence = sum(data['conf']) / len(data['conf']) if len(data['conf']) > 0 else 0
    logging.debug(f"Processed text with average confidence: {average_confidence}")
    return text, average_confidence

def process_images(input_dir, language, save_preprocessed, threshold, tesseract_cmd, tessdata_dir, check_orientation):
    tessdata_dir_config = r'--tessdata-dir "' + tessdata_dir + '"'
    output_file = os.path.join(input_dir, 'result.txt')

    with open(output_file, 'w', encoding='utf-8') as file_out:
        for index, filename in enumerate(sorted([f for f in os.listdir(input_dir) if f.endswith('.jpeg') or f.endswith('.jpg')]), start=1):
            full_path = os.path.join(input_dir, filename)
            img = preprocess_image(full_path, save_preprocessed, input_dir, threshold)
            if check_orientation :
                text, final_angle, confidence = check_orientations(img, language, tessdata_dir_config, tesseract_cmd, check_orientation)
            else:
                text, confidence = tesseract_ocr(img, language, tessdata_dir_config, tesseract_cmd)
                final_angle, = 0
            json_output = {"new_page": True, "number": index, "file": filename, "final_angle": final_angle, "confidence": confidence}
            file_out.write(f"'{json.dumps(json_output)}'\n{text}\n")
            logging.info(f"Processed {filename} with final angle: {final_angle}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_directory> [--language <lang_code>] [--save-preprocessed] [--threshold <int>] [--tessdata-path <path_to_tessdata>] [--check-orientation <int>]")
        sys.exit(1)

    input_dir = sys.argv[1]
    language = sys.argv[sys.argv.index('--language') + 1] if '--language' in sys.argv else "deu"
    save_preprocessed = '--save-preprocessed' in sys.argv
    threshold = int(sys.argv[sys.argv.index('--threshold') + 1]) if '--threshold' in sys.argv else 0
    check_orientation = int(sys.argv[sys.argv.index('--check_orientation') + 1]) if '--check_orientation' in sys.argv else 0
    if check_orientation > 2:
        print(f"Option `Check Orientation` must be 0 (no check) 1 (simple check) or 2 (thorough check) - supplied value {check_orientation} is not permitted, defaulting to 0!")
        check_orientation = 0;
    tesseract_cmd = find_tesseract_path()
    if '--tessdata-path' in sys.argv:
        tessdata_dir = sys.argv[sys.argv.index('--tessdata-path') + 1]
    else:
        tessdata_dir = os.path.join(os.path.dirname(tesseract_cmd), 'tessdata') if tesseract_cmd else ""

    logging.info(f"Arguments: Language: {language}, Save Preprocessed: {save_preprocessed}, Threshold: {threshold}, Check Orientation: {check_orientation}, Tessdata Path: {tessdata_dir}")
    process_images(input_dir, language, save_preprocessed, threshold, tesseract_cmd, tessdata_dir, check_orientation)

if __name__ == '__main__':
    main()
