# AxleroInternship_OmniBrain
# OmniBrain – AI Document Assistant

OmniBrain is an AI-powered document assistant that allows users to ask questions about complex PDF documents such as financial reports. It uses document ingestion, semantic search, LangGraph, Qdrant, RAG, Vision processing, and Self-RAG to provide relevant answers.

## Project Progress

### Week 1 – PDF Ingestion
- Built a PDF ingestion pipeline using PyMuPDF.
- Extracted text from PDF pages.
- Detected pages with low or missing text for visual processing.
- Generated structured JSON outputs for extracted content and visual pages.
- Tested the pipeline using a financial report.

### Week 2 – Streamlit UI
- Developed the Streamlit chat interface.
- Added user question input and chat history.
- Added display of final answers.
- Added document/page source information.
- Added support for displaying images/charts.
- Connected the UI with the LangGraph workflow.
- Added execution status without exposing private chain-of-thought.

### Week 3 – Backend & Retrieval
- Integrated the FastAPI backend.
- Implemented LangGraph-based workflow orchestration.
- Integrated Qdrant for semantic vector search.
- Implemented the Search Agent for document retrieval.
- Integrated document processing and Vision Agent.
- Implemented RAG-based context building and answer generation.
- Added Langfuse for workflow and retrieval observability.
- Tested document-question answering using a financial document.

### Week 4 – Self-RAG & Evaluation
- Implemented retrieval relevance checking.
- Added a similarity threshold of 0.40.
- Added query rewriting when the initial retrieval is not relevant.
- Limited retrieval to a maximum of two attempts.
- Added handling for cases where no relevant information is found.
- Tested relevant, poorly phrased, ambiguous, and unrelated questions.
- Recorded retrieval attempts and similarity scores.
- Identified borderline retrieval cases for future improvement.

## Self-RAG Flow

User Question  
↓  
Qdrant Retrieval  
↓  
Relevance Check  
↓  
Relevant → Context → Answer  
↓  
Not Relevant → Query Rewrite → Retrieval Again  
↓  
Still Not Relevant → No Relevant Information

## Technologies Used

- Python
- FastAPI
- Streamlit
- LangGraph
- Qdrant
- PyMuPDF
- RAG
- Hugging Face Transformers
- Langfuse
- Vision Model

## Current Status

The project currently supports PDF ingestion, semantic document retrieval, AI-based question answering, visual processing, Streamlit interaction, and Self-RAG-based retrieval evaluation.

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