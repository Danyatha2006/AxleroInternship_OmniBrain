# Week 4 – Self-RAG Evaluation Report

## 1. Objective

The objective of Week 4 was to test and evaluate the Self-RAG workflow implemented in OmniBrain.

The evaluation focused on:

- Testing different types of questions.
- Testing cases where the first retrieval gives irrelevant results.
- Testing cases where no relevant information exists in the document.
- Testing query rewriting and retrieval retry.
- Recording retrieval attempts and similarity scores.
- Identifying limitations and areas for future improvement.

---

## 2. Self-RAG Workflow

The implemented Self-RAG workflow follows this process:

User Question
↓
Qdrant Semantic Retrieval
↓
Relevance Check
↓
Relevant
→ Vision Processing
→ Context Building
→ Answer Generation

Not Relevant
→ Query Rewriting
→ Second Retrieval
→ Relevance Check

Still Not Relevant
→ No Relevant Information
→ End


The system allows a maximum of two retrieval attempts:

- Attempt 1: Original user query
- Attempt 2: Rewritten query

The relevance threshold is currently:

```text
0.40