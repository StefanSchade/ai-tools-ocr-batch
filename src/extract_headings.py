import argparse
import os
import json
import re
from fuzzywuzzy import fuzz

# Constants
TOC_KEYWORDS = ["Inhaltsverzeichnis", "Table of Contents", "TOC", "Inhalt"]
FUZZY_MATCH_THRESHOLD = 80  # percentage

# Helper functions
def fuzzy_match(line, keyword):
    return fuzz.partial_ratio(line.lower(), keyword.lower()) >= FUZZY_MATCH_THRESHOLD

def detect_heading_type(line):
    patterns = {
        'roman': r'^(M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))\.\s+(.*)$',
        'arabic_dotted': r'^(\d+(\.\d+)*)\s+(.*)$',
        'number_only': r'^(\d+)$',
        'page_number': r'(\d+(-\d+)?)$'
    }
    for typ, pat in patterns.items():
        match = re.match(pat, line.strip())
        if match:
            return typ, match.groups()
    return 'unknown', line.strip()

def process_toc(filename):
    headings = []
    collect_headings = False
    current_group = None
    heading_structure = []

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            if any(fuzzy_match(line, keyword) for keyword in TOC_KEYWORDS):
                collect_headings = True
                continue

            if collect_headings:
                if "// End TOC" in line:  # Placeholder for end of TOC detection
                    break

                heading_type, content = detect_heading_type(line)
                if heading_type == 'unknown':
                    continue

                if heading_type == 'number_only' and headings and 'numeral' not in headings[-1]:
                    headings[-1]['numeral'] = content
                else:
                    heading = {'text': content[-1] if isinstance(content, tuple) else content,
                               'type': heading_type,
                               'numeral': content[0] if isinstance(content, tuple) and heading_type != 'page_number' else None,
                               'page_or_range': content[1] if heading_type == 'page_number' else None}
                    headings.append(heading)
                    heading_structure.append(heading_type)

    # Post-process to determine levels based on structure
    for index, heading in enumerate(headings):
        heading['group_id'] = heading_structure[index]
        heading['level'] = heading_structure[:index].count(heading['group_id']) + 1

    return headings

def main():
    parser = argparse.ArgumentParser(description="Parse TOC from OCR Text")
    parser.add_argument("directory", help="Directory containing the OCR output files")
    args = parser.parse_args()

    toc_file = os.path.join(args.directory, "result.txt")
    headings = process_toc(toc_file)

    # Save to JSON
    with open(os.path.join(args.directory, "headings.json"), 'w', encoding='utf-8') as f:
        json.dump(headings, f, indent=4)

if __name__ == '__main__':
    main()
