import sys
import os
import re
import logging
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import pytesseract
import json
import argparse

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
    highest_confidence_after_basic_optimization = -1
    best_confidence_found = -1
    final_angle = 0

    # Initial broad check at major orientations
    for angle in orientations:
        rotated_image = image.rotate(angle, expand=True)
        text, confidence = tesseract_ocr(rotated_image, language, tessdata_dir_config, tesseract_cmd)
        if confidence > highest_confidence_after_basic_optimization:
            highest_confidence_after_basic_optimization = confidence
            best_text = text
            final_angle = angle
            # Break early if high enough confidence is found
            if confidence > HIGH_CONFIDENCE_THRESHOLD:
                break

    best_confidence_found = highest_confidence_after_basic_optimization
    logging.debug(f"Basic orientation correction result: Confidence={highest_confidence_after_basic_optimization}, orientation={final_angle}")

    # Detailed orientation check if the confidence threshold is not met
    if check_orientation == 2:
        # Check in one direction
        for adjustment in range(1, MAX_ROTATION_STEPS + 1):
            logging.debug(f"Fine optimization testing orientation {final_angle + adjustment * SMALL_ROTATION_STEP}")
            adjusted_image = image.rotate(final_angle + adjustment * SMALL_ROTATION_STEP, expand=True)
            adjusted_text, adjusted_confidence = tesseract_ocr(adjusted_image, language, tessdata_dir_config, tesseract_cmd)
            if adjusted_confidence > best_confidence_found:
                best_confidence_found = adjusted_confidence
                final_angle += adjustment * SMALL_ROTATION_STEP
                best_text = adjusted_text
            else:
                break  # Stop if no improvement

        # If no improvement was found in the initial direction, check the opposite direction
        if best_confidence_found == highest_confidence_after_basic_optimization:
            for adjustment in range(1, MAX_ROTATION_STEPS + 1):
                logging.debug(f"Fine optimization testing orientation {final_angle + adjustment * SMALL_ROTATION_STEP}")
                adjusted_image = image.rotate(final_angle - adjustment * SMALL_ROTATION_STEP, expand=True)
                adjusted_text, adjusted_confidence = tesseract_ocr(adjusted_image, language, tessdata_dir_config, tesseract_cmd)
                if adjusted_confidence > best_confidence_found:
                    best_confidence_found = adjusted_confidence
                    final_angle -= adjustment * SMALL_ROTATION_STEP
                    best_text = adjusted_text
                else:
                    break  # Stop if no improvement

    return best_text, final_angle, best_confidence_found

def tesseract_ocr(image, language, tessdata_dir_config, tesseract_cmd):
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    config = f'--oem 3 --psm 6 -l {language} {tessdata_dir_config}'
    data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)

    # Initialize a dictionary to hold text by lines
    lines = {}
    for i, word in enumerate(data['text']):
        #logging.debug(f"--------------- processing: word = {word} conf = {data['conf'][i]} line_num = {data['line_num'][i]}")
        if int(data['conf'][i]) > 60:  # Only consider confident recognitions
            line_num = data['line_num'][i]
            if line_num in lines:
                lines[line_num].append(word)
            else:
                lines[line_num] = [word]

    # Join lines preserving the text structure
    text = '\n'.join([' '.join(lines[line]) for line in sorted(lines.keys())])
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
                final_angle = 0
            json_output = {"new_page": True, "number": index, "file": filename, "final_angle": final_angle, "confidence": confidence}
            file_out.write(f"'{json.dumps(json_output)}'\n{text}\n")
            logging.info(f"Processed {filename} with final angle: {final_angle}")


def main():
    parser = argparse.ArgumentParser(description="Process some images.")
    parser.add_argument('input_directory', type=str, help='The directory containing images.')
    parser.add_argument('--language', type=str, default='deu', help='Language code for Tesseract OCR.')
    parser.add_argument('--save-preprocessed', action='store_true', help='Save preprocessed images.')
    parser.add_argument('--threshold', type=int, default=0, help='Threshold for image preprocessing.')
    parser.add_argument('--tessdata-path', type=str, help='Path to the tessdata directory.')
    parser.add_argument('--check-orientation', type=int, choices=[0, 1, 2], default=0, help='Check orientation with 0, 1, or 2.')

    args = parser.parse_args()

    # Accessing arguments via args object
    input_dir = args.input_directory
    language = args.language
    save_preprocessed = args.save_preprocessed
    threshold = args.threshold
    check_orientation = args.check_orientation
    tessdata_dir = args.tessdata_path if args.tessdata_path else os.path.join(os.path.dirname(find_tesseract_path()), 'tessdata')

    # Correct logging to use the variables from args
    logging.info(f"Arguments: Language: {language}, Save Preprocessed: {save_preprocessed}, Threshold: {threshold}, Check Orientation: {check_orientation}, Tessdata Path: {tessdata_dir}")

    # Assuming process_images function exists and is correctly implemented
    process_images(input_dir, language, save_preprocessed, threshold, find_tesseract_path(), tessdata_dir, check_orientation)

if __name__ == '__main__':
    main()