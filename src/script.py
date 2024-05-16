import sys
import os
from PIL import Image, ImageFilter, ImageOps
import pytesseract

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
    custom_config = r'--oem 3 --psm 3 -l ' + language + ' ' + tessdata_dir_config
    text = pytesseract.image_to_string(image, config=custom_config)
    return text

def process_images(input_dir, output_file, language, save_preprocessed, threshold):
    """Process all images in the directory and output OCR results to a file."""
    # Hardcode the path to the Tesseract executable
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\schades\AppData\Local\Tesseract-OCR\tesseract.exe'
    tessdata_dir_config = r'--tessdata-dir "C:\Users\schades\AppData\Local\Tesseract-OCR\tessdata"'

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
        print("Usage: python batch_ocr.py <input_directory> <output_file> [language_code] [--save-preprocessed] [threshold]")
    else:
        input_dir = sys.argv[1]
        output_file = sys.argv[2]
        language = 'deu'  # Default language
        save_preprocessed = False
        threshold = 0

        # Parse optional arguments
        for arg in sys.argv[3:]:
            if arg == '--save-preprocessed':
                save_preprocessed = True
            elif arg.isdigit():
                threshold = int(arg)
            elif len(arg) == 3 and arg.isalpha():
                language = arg

        process_images(input_dir, output_file, language, save_preprocessed, threshold)
