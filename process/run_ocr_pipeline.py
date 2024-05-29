import argparse
import logging
import os
import subprocess
from tqdm import tqdm

def run_script(script_name, args):
    command = ['python', script_name] + args
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Error running {script_name}: {result.stderr}")
        raise Exception(f"Error running {script_name}")
    return result.stdout

def main():
    parser = argparse.ArgumentParser(description='Run OCR processing pipeline.')
    parser.add_argument('directory', type=str, help='Directory for processing')
    parser.add_argument('--language', type=str, default='deu', help='Language code for OCR and dictionary')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='WARNING', help='Set the logging level')
    parser.add_argument('--threshold', type=int, default=0, help='Threshold for image preprocessing')
    parser.add_argument('--save-preprocessed', action='store_true', help='Save preprocessed images')
    parser.add_argument('--check-orientation', type=int, choices=[0, 1, 2], default=0, help='Check orientation with 0, 1, or 2')
    parser.add_argument('--tessdata-path', type=str, help='Path to the tessdata directory')

    args = parser.parse_args()

    # Set the logging level based on the command-line argument
    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format='%(asctime)s - %(levelname)s - %(message)s')

    # Determine default tessdata path if not provided
    tessdata_path = args.tessdata_path if args.tessdata_path else os.path.join(os.path.dirname(subprocess.run(['where', 'tesseract'], capture_output=True, text=True).stdout.strip()), 'tessdata')

    # Run OCR Step
    logging.info("Starting OCR step...")
    ocr_args = [
        args.directory,
        '--language', args.language,
        '--threshold', str(args.threshold),
        '--log-level', args.log_level
    ]
    if args.save_preprocessed:
        ocr_args.append('--save-preprocessed')
    #ocr_args.extend(['--tessdata-path', tessdata_path])
    ocr_args.extend(['--check-orientation', str(args.check_orientation)])

    run_script('ocr_batch.py', ocr_args)

    # Run Sanitization Step
    logging.info("Starting sanitization step...")
    sanitize_args = [
        args.directory,
        '--language', args.language,
        '--log-level', args.log_level
    ]

    run_script('sanitize_ocr.py', sanitize_args)

    logging.info("OCR processing pipeline completed successfully.")

if __name__ == "__main__":
    main()
