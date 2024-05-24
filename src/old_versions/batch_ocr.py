import sys
import os
import re
from PIL import Image, ImageFilter, ImageOps
import pytesseract

def find_tesseract_path():
    """Find the Tesseract executable in the system PATH."""
    paths = os.getenv('PATH').split(os.pathsep)
    tesseract_cmd = None
    for path in paths:
        if re.search(r'tesseract\\bin$', path, re.IGNORECASE):
            tesseract_cmd = os.path.join(path, 'tesseract.exe')
            break
    return tesseract_cmd

def preprocess_image(image_path, save_preprocessed, output_dir, threshold):
    """Pre-process the image to enhance OCR accuracy."""
    img = Image.open(image_path)
    img = img.convert('L')  # Convert to grayscale
    img = img.resize((img.width * 2, img.height * 2), Image.BICUBIC)  # Scale image
    img = img.filter(ImageFilter.MedianFilter())  # Apply median filter to remove noise
    if threshold > 0:
        img = img.point(lambda p: p > threshold and 255)  # Binarize the image

    if save_preprocessed:
        preprocessed_path = os.path.join(output_dir, 'preprocessed_images')
        if not os.path.exists(preprocessed_path):
            os.makedirs(preprocessed_path)
        img.save(os.path.join(preprocessed_path, os.path.basename(image_path)))

    return img

def tesseract_ocr(image, language, tessdata_dir_config):
    """Run OCR on the processed image with specified language."""
    if language == "none":
        custom_config = r'--oem 0 -l osd ' + tessdata_dir_config
    else:
        custom_config = r'--oem 3 --psm 3 -l ' + language + ' ' + tessdata_dir_config
    text = pytesseract.image_to_string(image, config=custom_config)
    return text

def process_images(input_dir, output_file, language, save_preprocessed, threshold, tesseract_cmd, tessdata_dir):
    """Process all images in the directory and output OCR results to a file."""
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    tessdata_dir_config = r'--tessdata-dir "' + tessdata_dir + '"'

    with open(output_file, 'w', encoding='utf-8') as file_out:
        for filename in sorted([f for f in os.listdir(input_dir) if f.endswith('.jpeg') or f.endswith('.jpg')]):
            full_path = os.path.join(input_dir, filename)
            try:
                img = preprocess_image(full_path, save_preprocessed, input_dir, threshold)
                text = tesseract_ocr(img, language, tessdata_dir_config)
                file_out.write(text + '\n')
                print(f"Processed {filename}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python batch_ocr.py <input_directory> <output_file> [language_code] [--save-preprocessed] [threshold] [--tesseract-path <path_to_tesseract>] [--tessdata-path <path_to_tessdata>]")
    else:
        input_dir = sys.argv[1]
        output_file = sys.argv[2]
        language = 'deu'  # Default language
        save_preprocessed = False
        threshold = 0
        tesseract_cmd = find_tesseract_path()
        tessdata_dir = ""

        i = 3
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == '--save-preprocessed':
                save_preprocessed = True
            elif arg.isdigit():
                threshold = int(arg)
            elif arg == '--tesseract-path' and i + 1 < len(sys.argv):
                tesseract_cmd = sys.argv[i + 1]
                i += 1
            elif arg == '--tessdata-path' and i + 1 < len(sys.argv):
                tessdata_dir = sys.argv[i + 1]
                i += 1
            elif len(arg) == 3 and arg.isalpha():
                language = arg
            i += 1

