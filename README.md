# AxleroInternship_OmniBrain
# Basic PDF Ingestion Pipeline

## Project Overview

This project implements a basic PDF ingestion pipeline for a Smart Document Assistant.

The pipeline accepts a PDF document, extracts its text page-by-page, performs basic validation, identifies pages with very little extracted text, and saves the extracted content as a text file.

The pipeline is designed to handle large documents such as financial reports.

## Project Structure

```text
Project 1/
├── data/
│   ├── input/
│   │   └── finance.pdf
│   └── output/
│       └── finance.txt
├── src/
│   └── pdf_loader.py
├── venv/
├── main.py
└── README.md
```

## Technologies Used

* Python
* PyMuPDF

## Pipeline

```text
PDF
 ↓
Input Folder
 ↓
PDF Validation
 ↓
Text Extraction
 ↓
Page-level Metadata
 ↓
Low-text Page Detection
 ↓
Text Output
```

## Features

* Reads PDF files from the input folder
* Extracts text page-by-page
* Preserves page numbers
* Counts characters extracted from each page
* Detects pages with fewer than 50 characters
* Handles missing PDF files
* Validates the PDF file extension
* Handles errors while opening PDFs
* Saves extracted text to the output folder

## How to Run

### 1. Activate the virtual environment

On Windows:

```bash
venv\Scripts\activate
```

### 2. Install the dependency

```bash
pip install pymupdf
```

### 3. Place the PDF

Put the PDF you want to process inside:

```text
data/input/
```

### 4. Update the PDF path

In `main.py`, specify the PDF filename:

```python
pdf_path = "data/input/finance.pdf"
```

### 5. Run the pipeline

From the project root:

```bash
python main.py
```

### 6. Output

The extracted text is saved in:

```text
data/output/finance.txt
```

## Testing

The pipeline was tested using a large financial PDF to verify that it can successfully open the document and extract text page-by-page.

The pipeline also reports pages where fewer than 50 characters of text were extracted. These pages may contain tables, images, scanned content, or very little text.

## Scope

This project focuses only on the **basic PDF ingestion stage**.

It does not currently include:

* OCR
* Text chunking
* Embeddings
* Vector databases
* Retrieval-Augmented Generation (RAG)
* AI question answering
*