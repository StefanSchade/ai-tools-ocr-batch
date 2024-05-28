from prompt_toolkit.key_binding import KeyBindings
import sys
import os
import logging
from prompt_toolkit.application import Application
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout import Layout

# Setup logging for debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
class InteractiveHeadingsEditor:
    def __init__(self, headings):
        self.headings = headings
        initial_text = self.format_headings_for_display()
        self.text_area = TextArea(text=initial_text)

        # Setup key bindings
        self.key_bindings = KeyBindings()
        self.setup_key_bindings()

    def format_headings_for_display(self):
        return '\n'.join([f"{h['text']} - Level: {h['level']}" for h in self.headings])

    def setup_key_bindings(self):
        @self.key_bindings.add('c-c')  # Ctrl-C to exit
        def _(event):
            event.app.exit()

        @self.key_bindings.add('escape')  # Esc to exit
        def _(event):
            event.app.exit()

    def run(self):
        layout = Layout(container=self.text_area)
        app = Application(layout=layout, full_screen=True, key_bindings=self.key_bindings)
        app.run()


def main():
    # Example usage of the InteractiveHeadingsEditor
    example_headings = [{'text': 'Chapter 1', 'level': 1}, {'text': 'Section 1.1', 'level': 2}]
    editor = InteractiveHeadingsEditor(example_headings)
    editor.run()

if __name__ == '__main__':
    main()
