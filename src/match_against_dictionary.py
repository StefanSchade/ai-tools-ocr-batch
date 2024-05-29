import argparse
import enchant
from enchant.checker import SpellChecker
import os

def correct_text(input_text, lang):
    """Correct OCR errors and handle end-line hyphens based on the given language."""
    checker = SpellChecker(lang)
    corrected_text = []
    words = input_text.replace('\n', ' ').split()
    i = 0
    while i < len(words):
        word = words[i]
        if word.endswith('-'):
            # Try to combine with the next word to handle end-line hyphens
            if i + 1 < len(words):
                next_word = words[i + 1]
                combined_word = word[:-1] + next_word  # Attempt to combine words without the hyphen
                if checker.check(combined_word):
                    # If combined word is correct, append and skip the next word
                    corrected_text.append(combined_word)
                    i += 1  # Skip the next word
                else:
                    # If not correct, just append the word without hyphen
                    corrected_text.append(word[:-1])
                i += 1
                continue
        # Append the current word if it does not end with a hyphen or after handling hyphen
        corrected_text.append(word)
        i += 1
    return ' '.join(corrected_text)

def process_file(input_file, output_file, lang):
    """Read the input file, process it, and write the output to the output file."""
    with open(input_file, 'r', encoding='utf-8') as file:
        input_text = file.read()

    corrected_text = correct_text(input_text, lang)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(corrected_text)

def main():
    parser = argparse.ArgumentParser(description="Process OCR results and correct common OCR errors.")
    parser.add_argument("dir", help="Directory containing the OCR result file")
    parser.add_argument("--lang", default="en_US", choices=enchant.list_languages(),
                        help="Language for the spell checker to use")
    args = parser.parse_args()

    input_path = os.path.join(args.dir, "result.txt")
    output_path = os.path.join(args.dir, "result_dictionary_matching.txt")

    print("Installed languages:")
    print(enchant.list_languages())
    print("All languages:")
    print(enchant.list_languages())

    if not os.path.exists(input_path):
        print(f"Error: {input_path} does not exist.")
        return

    process_file(input_path, output_path, args.lang)
    print(f"Processed text has been saved to {output_path}.")

if __name__ == "__main__":
    main()
