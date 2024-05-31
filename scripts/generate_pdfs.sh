#!/bin/bash

# Navigate to the docs directory
cd /workspace/docs

# Generate PDFs from all Asciidoc files
for file in *.adoc; do
  asciidoctor-pdf "$file" -o "/workspace/target/${file%.adoc}.pdf"
done