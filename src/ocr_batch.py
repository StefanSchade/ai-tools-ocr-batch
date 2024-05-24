import sys
import os
import re
import logging
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
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
    img = Image.open(image_path)
    img = img.convert('L')
    img = img.resize((img.width * 2, img.height * 2), Image.BICUBIC)
    img = img.filter(ImageFilter.MedianFilter())
    if threshold > 0:
        img = img.point(lambda p: p > threshold and 255)
    return img

def check_orientations(image, language, tessdata_dir_config, tesseract_cmd):
    """Rotate image in all four orientations and perform OCR, returning the best result based on confidence."""
    orientations = [0, 90, 180, 270]
    best_text = ''
    highest_confidence = -1

    for angle in orientations:
        rotated_image = image.rotate(angle, expand=True)
        text, confidence = tesseract_ocr(rotated_image, language, tessdata_dir_config, tesseract_cmd)
        if confidence > highest_confidence:
            highest_confidence = confidence
            best_text = text
    return best_text

def tesseract_ocr(image, language, tessdata_dir_config, tesseract_cmd):
    """Run OCR on the processed image with specified language and return text with confidence score."""
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    config = f'--oem 3 --psm 3 -l {language} {tessdata_dir_config}'
    data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
    text = ' '.join([data['text'][i] for i in range(len(data['text'])) if data['conf'][i] > 60])
    if len(data['conf']) > 0:
        average_confidence = sum(data['conf']) / len(data['conf'])
    else:
        average_confidence = 0
    return text, average_confidence


def process_images(input_dir, language, save_preprocessed, threshold, tessdata_dir, check_orientation):
    """Process all images in the directory, potentially checking orientation, and output OCR results to a file."""
    output_file = os.path.join(input_dir, "result.txt")
    tessdata_dir_config = f'--tessdata-dir "{tessdata_dir}"'
    tesseract_cmd = find_tesseract_path()

    with open(output_file, 'w', encoding='utf-8') as file_out:
        for index, filename in enumerate(sorted([f for f in os.listdir(input_dir) if f.endswith(('.jpeg', '.jpg', '.png'))])):
            full_path = os.path.join(input_dir, filename)
            img = preprocess_image(full_path, save_preprocessed, input_dir, threshold)
            if check_orientation:
                text = check_orientations(img, language, tessdata_dir_config, tesseract_cmd)
            else:
                text, _ = tesseract_ocr(img, language, tessdata_dir_config, tesseract_cmd)
            file_out.write(f"// {{\"new_page\": true, \"page_number\": {index + 1}, \"page_file\": \"{filename}\"}}\n")
            file_out.write(text + '\n')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_directory> [language_code] [--save-preprocessed] [threshold] [--tessdata-path <path_to_tessdata>] [--check-orientation]")
        sys.exit(1)

    input_dir = sys.argv[1]
    language = 'eng'  # Default language
    save_preprocessed = False
    threshold = 0
    tessdata_dir = ""
    check_orientation = False

    for arg in sys.argv[2:]:
        if arg == '--save-preprocessed':
            save_preprocessed = True
        elif arg.isdigit():
            threshold = int(arg)
        elif arg.startswith('--tessdata-path'):
            tessdata_dir = arg.split('=')[1]
        elif len(arg) == 3 and arg.isalpha():
            language = arg
        elif arg == '--check-orientation':
            check_orientation = True

    process_images(input_dir, language, save_preprocessed, threshold, tessdata_dir, check_orientation)
