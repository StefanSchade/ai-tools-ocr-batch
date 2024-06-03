import argparse
import os
import json
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.widgets import Button, TextArea

class InteractiveHeadingsEditor:
    def __init__(self, headings):
        self.headings = headings
        self.current_index = 0
        self.status = TextArea(focusable=False, text="Use Arrow keys to navigate. Tab/Shift-Tab to change level. 'x' to toggle delete.")

    def display_headings(self):
        items = []
        for index, heading in enumerate(self.headings):
            selected = "->" if index == self.current_index else "  "
            deletion_status = "[DELETED]" if heading.get("deleted", False) else ""
            items.append(f"{selected} Level {heading['level']}: {heading['text']} {deletion_status}")
        return items

    def run(self):
        bindings = KeyBindings()

        @bindings.add('up')
        def _(event):
            self.current_index = max(0, self.current_index - 1)
            get_app().invalidate() # refresh UI after changes

        @bindings.add('down')
        def _(event):
            self.current_index = min(len(self.headings) - 1, self.current_index + 1)
            get_app().invalidate() # refresh UI after changes

        @bindings.add('tab')
        def _(event):
            self.headings[self.current_index]['level'] += 1
            get_app().invalidate() # refresh UI after changes

        @bindings.add('s-tab')
        def _(event):
            self.headings[self.current_index]['level'] = max(1, self.headings[self.current_index]['level'] - 1)
            get_app().invalidate() # refresh UI after changes

        @bindings.add('x')
        def _(event):
            self.headings[self.current_index]['deleted'] = not self.headings[self.current_index].get('deleted', False)
            get_app().invalidate() # refresh UI after changes

        @bindings.add('enter')
        def _(event):
            event.app.exit()

        # Use FormattedTextControl to dynamically update the text area content
        text_control = FormattedTextControl(self.display_headings)
        text_window = Window(content=text_control, wrap_lines=True)

        layout = Layout(HSplit([text_window, self.status]))

        app = Application(layout=layout, key_bindings=bindings, full_screen=True)
        app.run()


def load_headings(scan_dir):
    headings_file = os.path.join(scan_dir, 'headings.json')
    try:
        with open(headings_file, 'r') as file:
            headings = json.load(file)
        print("Headings loaded from file.")
    except (IOError, ValueError) as e:
        print(f"Failed to load headings from file: {e}. Using default headings.")
        headings = [
            {'text': 'Chaptexr 1', 'level': 1, 'deleted': False},
            {'text': 'Sectioxn 1.1', 'level': 2, 'deleted': False},
            {'text': 'Sectioxn 1.2', 'level': 2, 'deleted': False}
        ]
    return headings

def save_headings(headings, scan_dir):
    headings_file = os.path.join(scan_dir, 'headings.json')
    with open(headings_file, 'w') as file:
        json.dump(headings, file, indent=4)
    print(f"Headings saved to {headings_file}.")


def main():
    parser = argparse.ArgumentParser(description="OCR Output Editor")
    parser.add_argument("scan_dir", help="Directory containing the OCR output files and target directory for the output")
    args = parser.parse_args()

    # Load or simulate headings data
    headings = load_headings(args.scan_dir)  # This function needs to be defined based on your OCR results

    editor = InteractiveHeadingsEditor(headings)
    editor.run()

    # Save the edited headings
    save_headings(headings, args.scan_dir)  # This function also needs to be defined

if __name__ == '__main__':
    main()
