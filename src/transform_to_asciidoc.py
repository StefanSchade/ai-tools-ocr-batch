import json
import re
import sys

# Constants for header detection
HEADER_KEY_WORDS = ["KAPITEL", "VORWORT", "EINLEITUNG", "INHALTSVERZEICHNIS"]
HEADER_CHARS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ')

def is_header(line):
    words = line.split()
    # Check if the majority of the words in the line are uppercase and if it contains typical header keywords
    if all(word.isupper() for word in words if len(word) > 1):
        return any(keyword in line for keyword in HEADER_KEY_WORDS) or all(char in HEADER_CHARS for char in line.replace(" ", ""))
    return False

def parse_json_line(line):
    try:
        return json.loads(line.strip("'"))
    except json.JSONDecodeError:
        return None

def convert_to_asciidoc(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            if line.startswith("'"):  # Metadata line
                metadata = parse_json_line(line)
                if metadata:
                    outfile.write(f"// meta: {json.dumps(metadata)}\n")
                continue
            if is_header(line.strip()):
                outfile.write(f"== {line.strip()}\n")
            else:
                outfile.write(line)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python transform_to_asciidoc.py <input_file> <output_file>")
        sys.exit(1)
    input_file, output_file = sys.argv[1], sys.argv[2]
    convert_to_asciidoc(input_file, output_file)
