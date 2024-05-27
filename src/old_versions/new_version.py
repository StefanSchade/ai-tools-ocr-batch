import sys
import os
import re
from PIL import Image, ImageFilter, ImageOps
import pytesseract

def find_tesseract_path():
    """Find the Tesseract executable in the system PATH."""
    paths = os.getenv('PATH').split(os.pathsep)
    for path in paths:
        if re.search(r'tesseract\\bin$', path, re.IGNORECASE):
            return os.path.join(path, 'tesseract.exe')
    return None

def preprocess_image(image_path, save_preprocessed, output_dir, threshold):
    """Pre-process the image to enhance OCR accuracy."""
    img = Image.open(image_path)
    img = img.convert('L')  # Convert to grayscale
    img = img.resize((img.width * 2, img.height * 2), Image.BICUBIC)  # Scale image
    img = img.filter(ImageFilter.MedianFilter())  # Apply median filter to remove noise
    if threshold > 0:
        img = img.point(lambda p: p > threshold and 255)

    if save_preprocessed:
        preprocessed_path = os.path.join(output_dir, 'preprocessed_images')
        os.makedirs(preprocessed_path, exist_ok=True)
        img.save(os.path.join(preprocessed_path, os.path.basename(image_path)))

    return img

def get_best_orientation(image, language, config):
    """Determine the best orientation based on OCR confidence scores."""
    best_confidence = -1
    best_orientation = 0
    for angle in [0, 90, 180, 270]:
        rotated_img = image.rotate(angle, expand=True)
        data = pytesseract.image_to_data(rotated_img, config=config, output_type=pytesseract.Output.DICT)
        valid_scores = [int(conf) for conf, text in zip(data['conf'], data['text']) if text.strip() and int(conf) > 0]
        avg_confidence = sum(valid_scores) / len(valid_scores) if valid_scores else 0

        if avg_confidence > best_confidence:
            best_confidence = avg_confidence
            best_orientation = angle

    return best_orientation

def tesseract_ocr(image, language, tessdata_dir_config):
    """Run OCR on the processed image with specified language."""
    config = f'--oem 3 --psm 3 -l {language} {tessdata_dir_config}'
    return pytesseract.image_to_string(image, config=config)

def process_images(input_dir, output_file, language, save_preprocessed, threshold, tesseract_cmd, tessdata_dir, check_orientation=False):
    """Process all images in the directory and output OCR results to a file."""
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    tessdata_dir_config = f'--tessdata-dir "{tessdata_dir}"'

    with open(output_file, 'w', encoding='utf-8') as file_out:
        for filename in sorted(os.listdir(input_dir)):
            if filename.lower().endswith(('.jpeg', '.jpg', '.png')):
                full_path = os.path.join(input_dir, filename)
                img = preprocess_image(full_path, save_preprocessed, input_dir, threshold)
                if check_orientation:
                    best_angle = get_best_orientation(img, language, tessdata_dir_config)
                    img = img.rotate(best_angle, expand=True)
                text = tesseract_ocr(img, language, tessdata_dir_config)
                file_out.write(text + '\n')

if __name__ == '__main__':
    input_dir = sys.argv[1]
    output_file = sys.argv[2]
    language = 'eng'  # Default to English, replace 'eng' with 'deu' if needed
    save_preprocessed = '--save-preprocessed' in sys.argv
    threshold = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    tesseract_cmd = find_tesseract_path()
    tessdata_dir = sys.argv[7] if len(sys.argv) > 7 else ""
    check_orientation = '--check-orientation' in sys.argv

    process_images(input_dir, output_file, language, save_preprocessed, threshold, tesseract_cmd, tessdata_dir, check_orientation)
