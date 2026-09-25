# OmniBrain Frontend — Complete UI/UX

A polished React/Vite frontend for the OmniBrain Agentic Multi-Modal RAG Orchestrator.

## What is included

- PDF upload with drag-and-drop
- Document processing / indexing status
- AI document chat
- Suggested questions and quick actions
- Exact-page citation cards
- Retrieved image / chart references
- Image gallery and extracted-visual panel
- Document analytics: pages, words, sentences, tables, images
- Agent routing / reasoning trace panel
- Self-RAG retry indicator
- Guardrails status
- Latency / token / retrieval metrics
- Conversation history in the current session
- Responsive desktop + mobile layout
- Demo mode so the UI can be shown before backend integration
- One central API adapter for easy FastAPI integration

## Run

```bash
npm install
npm run dev
```

Then open:

http://localhost:5173

## Backend integration

Create `.env` from `.env.example`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

The frontend already calls:

- `POST /api/v1/documents/upload`
- `GET /api/v1/documents/{document_id}/status`
- `POST /api/v1/chat`
- `GET /api/v1/chat/{document_id}/history`
- `GET /api/v1/documents/{document_id}/analytics`
- `GET /api/v1/documents/{document_id}/images`

If your group's FastAPI routes use different names, change only the `api()` calls in `src/main.jsx`.

Until those extra analytics/image endpoints are available, the UI falls back gracefully and keeps the rest of the workspace usable.
