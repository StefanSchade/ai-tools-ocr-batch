import argparse
import logging
import os
import re
from tqdm import tqdm

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class CustomDictionary:
    def __init__(self, file_path):
        self.words = set()
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.split('/')[0].strip()  # Extract the word before the '/'
                self.words.add(word)

    def check(self, word):
        return word in self.words

    def check_with_endings(self, word, endings):
        if word in self.words:
            return True
        for ending in endings:
            if word.endswith(ending) and word[:-len(ending)] in self.words:
                return True
        return False

def load_dict(language):
    if language == 'deu':
        return CustomDictionary('C:/Users/schades/.dictionaries/german.dic')
    else:
        raise ValueError(f"Unsupported language: {language}")

def handle_hyphens_and_join_lines(lines, dictionary, endings):
    new_lines = []
    skip_next = False
    joined_line = ""

    for i in tqdm(range(len(lines)), desc='Handling Hyphens and Joining Lines'):
        current_line = lines[i].rstrip()
        if i < len(lines) - 1:
            next_line = lines[i + 1].lstrip()
        else:
            next_line = ""

        if current_line.endswith('-'):
            logging.debug(f"Found hyphen at end of line {i}: {current_line}")
            prev_word = re.findall(r'\b\w+\b(?=-$)', current_line)
            prev_word = prev_word[-1] if prev_word else ''
            first_word_next_line = next_line.split()[0] if next_line.split() else ''
            combined_word = prev_word + first_word_next_line
            logging.debug(f"Trying to combine '{prev_word}' with '{first_word_next_line}' to form '{combined_word}'")
            if dictionary.check_with_endings(combined_word, endings):
                logging.debug(f"Combined word '{combined_word}' is valid.")
                new_line = current_line[:-len(prev_word)-1] + combined_word + next_line[len(first_word_next_line):]
                new_lines.append(new_line)
                logging.debug(f"New combined line: {new_line}")
                skip_next = True
            else:
                logging.debug(f"Combined word '{combined_word}' is not valid. Keeping lines separate.")
                new_lines.append(current_line + next_line)
                skip_next = True
        elif re.match(r'\b\w+s-$', current_line):
            logging.debug(f"Found potential compound word with hyphen at end of line {i}: {current_line}")
            prev_word = re.findall(r'\b\w+\b(?=s-$)', current_line)
            prev_word = prev_word[-1] if prev_word else ''
            first_word_next_line = next_line.split()[0] if next_line.split() else ''
            combined_word = prev_word + 's' + first_word_next_line
            logging.debug(f"Trying to combine '{prev_word}s' with '{first_word_next_line}' to form '{combined_word}'")
            if dictionary.check_with_endings(prev_word, endings) and dictionary.check_with_endings(first_word_next_line, endings):
                logging.debug(f"Compound word '{combined_word}' is valid.")
                new_line = current_line[:-len(prev_word)-2] + prev_word + first_word_next_line.lower() + next_line[len(first_word_next_line):]
                new_lines.append(new_line)
                logging.debug(f"New compound combined line: {new_line}")
                skip_next = True
            else:
                logging.debug(f"Compound word '{combined_word}' is not valid. Keeping lines separate.")
                new_lines.append(current_line + next_line)
                skip_next = True
        else:
            # Join the current line with the next if it does not end with a hyphen
            if joined_line:
                joined_line += " " + current_line
            else:
                joined_line = current_line

            if not current_line.endswith('-'):
                if next_line:
                    joined_line += " " + next_line
                new_lines.append(joined_line.strip())
                joined_line = ""
            else:
                new_lines.append(joined_line.strip())
                joined_line = ""

    if joined_line:
        new_lines.append(joined_line.strip())

    return new_lines

def sanitize_text(input_file, output_file, dictionary, endings):
    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    # Handle hyphens and join lines
    sanitized_lines = handle_hyphens_and_join_lines(lines, dictionary, endings)

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
    endings = ['e', 'en', 's']

    sanitize_text(input_file, output_file, dictionary, endings)

if __name__ == "__main__":
    main()
