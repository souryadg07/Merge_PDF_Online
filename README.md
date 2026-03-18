# PDF Merger (Lossless)

A simple command-line tool to merge multiple PDF files without any loss in quality.
Built using `pypdf`, it preserves original content including images, fonts, and vector graphics.

## Features
- Lossless PDF merging
- Auto-detects PDFs in the current directory
- Supports files and folders as input
- Optional interactive reordering
- Preserves metadata from the first PDF

## Installation

pip install pypdf

## Usage

### 1. Interactive mode (auto-detect PDFs)
python3 merge_pdfs.py

### 2. Merge specific files
python3 merge_pdfs.py file1.pdf file2.pdf -o merged.pdf

### 3. Merge all PDFs in a folder
python3 merge_pdfs.py /path/to/folder/ -o output.pdf

### 4. Skip reordering prompt
python3 merge_pdfs.py *.pdf --no-reorder -o merged.pdf

## Notes
- If no output file is specified, you’ll be prompted (default: merged.pdf)
- Non-PDF files are ignored automatically
- Invalid or unreadable PDFs are skipped