import argparse
import logging
import os
import re
from tqdm import tqdm

# Setup logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

class CustomDictionary:
    def __init__(self, file_path):
        self.words = set()
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.split('/')[0].strip()  # Extract the word before the '/'
                self.words.add(word)

    def check(self, word):
        return word in self.words

def load_dict(language):
    if language == 'deu':
        return CustomDictionary('C:/Users/schades/.dictionaries/german.dic')
    else:
        raise ValueError(f"Unsupported language: {language}")

def handle_hyphens(lines, dictionary):
    new_lines = []
    skip_next = False
    for i in tqdm(range(len(lines) - 1), desc='Handling Hyphens'):
        if skip_next:
            skip_next = False
            continue
        current_line = lines[i].rstrip()
        next_line = lines[i + 1].lstrip()
        if current_line.endswith('-'):
            combined_word = current_line[:-1] + next_line.split()[0]
            if dictionary.check(combined_word):
                new_lines.append(current_line[:-1] + next_line)
                skip_next = True
            else:
                new_lines.append(current_line)
        else:
            new_lines.append(current_line)
    if not skip_next:
        new_lines.append(lines[-1])
    return new_lines

def sanitize_text(input_file, output_file, dictionary):
    def split_tokens(text):
        return re.findall(r'\w+|[^\w\s]', text, re.UNICODE)

    def join_tokens(tokens):
        result = []
        for i in range(len(tokens)):
            if i > 0 and re.match(r'\w', tokens[i]) and re.match(r'\w', tokens[i - 1]):
                result.append(' ')
            result.append(tokens[i])
        return ''.join(result)

    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    # Handle hyphens first before any other processing
    lines = handle_hyphens(lines, dictionary)

    sanitized_lines = []
    for line in tqdm(lines, desc='Sanitizing Text'):
        tokens = split_tokens(line)
        sanitized_lines.append(join_tokens(tokens))

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(sanitized_lines))

def main():
    parser = argparse.ArgumentParser(description='Sanitize OCR results')
    parser.add_argument('directory', type=str, help='Directory for processing')
    parser.add_argument('--language', type=str, default='deu', help='Language code for dictionary')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='WARNING', help='Set the logging level')

    args = parser.parse_args()

    # Set the logging level based on the command-line argument
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

    input_file = os.path.join(args.directory, 'ocr_result.txt')
    output_file = os.path.join(args.directory, 'sanitized_result.txt')

    dictionary = load_dict(args.language)

    sanitize_text(input_file, output_file, dictionary)

if __name__ == "__main__":
    main()
