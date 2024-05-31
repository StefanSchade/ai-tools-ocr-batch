# Use an official Ubuntu as a parent image
FROM ubuntu:latest

# Install required tools
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    vim \
    python3 \
    python3-pip \
    python3-venv \
    tesseract-ocr \
    asciidoctor \
    bash

# Set the working directory
WORKDIR /workspace

# Create and activate a virtual environment
RUN python3 -m venv /workspace/venv

# Set environment variables for the virtual environment
ENV PATH="/workspace/venv/bin:$PATH"

# Run bash by default
CMD ["bash"]
