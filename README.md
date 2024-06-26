<img src="README/windows_typewriter.webp" width="300"/>

# OCR Batch

This repository was meant for a collection of scripts designed to automate the Optical Character Recognition (OCR) of images and various post-processing tasks.

While the first step (OCR processing) was returning very promising results, already the second step of improving the output by reconciling it with  returned underwhelming results. One reason is that the library I use for this (Enchanted) is not feature complete in Windows. [See here](https://pyenchant.github.io/pyenchant/api/enchant.pypwl.html)

I will therefore start afresh with developing in a container which gives me access to the Linux implementation of these libs. As the windows version worked quite nicely in step 1 and some users might not have access to a Docker environment I leave this repo available.

Maybe at a later point I will come back with the experience I gathered with the new approach.

## Scripts Included

* Overall Script `run_ocr_pipeline` provides one frontend for the whole pipeline **individual scripts can also be called by themselves**
* 1st step `ocr_batch.py` first step of the pipeline processes a batch of jpg images 
* 2nd step `match_against_dictionary` improves ocr result by applying a spell-check
  * Correct OCR imperfections 
  * Remove line-end hyphens while retaining   

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
   - make sure to also install the training data for the languages you want to use.

3. **Python Libraries Installation:**
   - Install the required Python libraries using pip:
     ```
     pip install Pillow pytesseract pyenchant tqdm
     ```

#### Usage
To use the `ocr_batch.py` script, navigate to the script's directory in your terminal and execute the following command:

```
python ocr_batch.py <input_directory> [options]
```

**Options:**
- `<input_directory>`: Mandatory, provide the path to the direcotry where the jpgs to be processed and the output (`result.txt`) will be located  
- `--language <lang_code>`: Sets the OCR language (default is 'deu' for German). 
- `--save-preprocessed`: Saves preprocessed images for review.
- `--threshold <int>`: Sets a pixel intensity threshold for image binarization.
- `--tessdata-path <path_to_tessdata>`: Specifies a custom path to the tessdata directory. If none is specified we do a plausible guess.
- `--check-orientation <level>`: Sets the level of orientation checking (0, 1, or 2).
- `--log-level <level>`: String that specifies the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

**Example:**
```
python ocr_batch.py "./images" --language eng --save-preprocessed --threshold 100 --check-orientation 1
```

#### Fine tuning the scan result

In the script, the statement `config = f'--oem 3 --psm 6 -l {language} {tessdata_dir_config}'` configures tesseract. Here you can influence the scan parameters. As they do not change from scan to scan, I decided against externalizing them as a command line parameter. However if you are unhappy with the scan result it is worth playing with this configuration. 

for instance a parameter of `--psm 3` for me resulted in an output as one block of text without the line breaks of the original. If this is what you want it might be worth adjusting this in the script. Presently this is not externalized as a parameter.

```
To list out the 14 PSMs in Tesseract, just supply the --help-psm argument to the tesseract binary:

Tesseract Page Segmentation Modes (PSMs) Explained: How to Improve Your OCR Accuracy
$ tesseract --help-psm
Page segmentation modes:
0    Orientation and script detection (OSD) only.
1    Automatic page segmentation with OSD.
2    Automatic page segmentation, but no OSD, or OCR. (not implemented)
3    Fully automatic page segmentation, but no OSD. (Default)
4    Assume a single column of text of variable sizes.
5    Assume a single uniform block of vertically aligned text.
6    Assume a single uniform block of text.
7    Treat the image as a single text line.
8    Treat the image as a single word.
9    Treat the image as a single word in a circle.
10    Treat the image as a single character.
11    Sparse text. Find as much text as possible in no particular order.
12    Sparse text with OSD.
13    Raw line. Treat the image as a single text line,
bypassing hacks that are Tesseract-specific.
```






