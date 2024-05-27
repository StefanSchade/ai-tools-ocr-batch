
# OCR Batch Processing Tools

This repository contains a collection of scripts designed to automate the Optical Character Recognition (OCR) of images and perform various post-processing tasks on the recognized text. These tools are intended to streamline the processing of large batches of images into editable and analyzable text formats.

## Scripts Included

### 1. OCR Image Processing (`ocr_batch.py`)

#### Purpose
The `ocr_batch.py` script automates the process of converting images containing textual content into plain text files using OCR technology. It is designed to handle large volumes of images and includes features for optimizing text recognition accuracy through image rotation and quality checks.

#### General Strategy
The script employs Tesseract OCR to extract text from images. It enhances the images' quality, adjusts their orientation based on OCR confidence scores, and outputs the results with optional metadata about the process. The script allows for varying levels of orientation checks to balance between accuracy and processing time.

#### Prerequisites
- **Python Environment:** The script is written in Python and requires Python 3.x installed on your system.
- **Tesseract OCR:** Tesseract must be installed and accessible from your system's PATH to allow the script to invoke the OCR engine.
- **Python Libraries:** Several Python libraries are required, including `PIL` (Pillow), `pytesseract`, and `json`. These can be installed via pip.

#### Installation Guide
1. **Python Installation:**
   - Ensure Python 3.x is installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

2. **Tesseract OCR Installation:**
   - Install Tesseract OCR by following the instructions on the [Tesseract GitHub page](https://github.com/tesseract-ocr/tesseract). Make sure to add the Tesseract directory to your system's PATH.
   - Detailed installation guides for various operating systems can be found on the linked GitHub repository.

3. **Python Libraries Installation:**
   - Install the required Python libraries using pip:
     ```
     pip install Pillow pytesseract
     ```

#### Usage
To use the `ocr_batch.py` script, navigate to the script's directory in your terminal and execute the following command:

```
python ocr_batch.py <input_directory> [options]
```

**Options:**
- `--language <lang_code>`: Sets the OCR language (default is 'deu' for German).
- `--save-preprocessed`: Saves preprocessed images for review.
- `--threshold <int>`: Sets a pixel intensity threshold for image binarization.
- `--tessdata-path <path_to_tessdata>`: Specifies a custom path to the tessdata directory.
- `--check-orientation <level>`: Sets the level of orientation checking (0, 1, or 2).

**Example:**
```
python ocr_batch.py "./images" --language eng --save-preprocessed --threshold 100 --check-orientation 1
```
