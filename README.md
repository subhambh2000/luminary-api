# Luminary
Luminary is a Retrieval-Augmented Generation (RAG) framework designed to build intelligent, context-aware chatbots from
your personal knowledge base. It ingests documents, chunks them intelligently, embeds them using state-of-the-art
models, and retrieves relevant context to augment LLM responses. Whether you're building a research assistant, knowledge
base chatbot, or domain-specific QA system, Luminary provides a scalable, easy-to-use pipeline to combine the power of
semantic search with generative AI.

## Architecture Overview
```
┌─────────────────┐
│ User Query      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ Ingest Pipeline             │
├─────────────────────────────┤
│ 1. Read Documents           │
│ 2. Chunk (Semantic)         │
│ 3. Embed (Qwen3-Embedding)  │
│ 4. Store in Qdrant          │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Retrieval Pipeline          │
├─────────────────────────────┤
│ 1. Embed Query              │
│ 2. Search Similar Chunks    │
│ 3. Rank & Filter (threshold)│
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Generation Pipeline         │
├─────────────────────────────┤
│ 1. Build Context            │
│ 2. Stream Response (Groq)   │
│ 3. Store in Session History │
└────────┬────────────────────┘
         │
         ▼
┌──────────────────┐
│ User Response    │
└──────────────────┘
```

## Tech Stack
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs
- **Vector Database**: [Qdrant](https://qdrant.tech/) - High-performance vector search database
- **Embeddings**: [Qwen/Qwen3-Embedding-0.6B](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B) - Lightweight, efficient embedding model
- **LLM**: [Groq](https://groq.com/) - Fast inference for LLaMA 3.3 70B
- **NLP**: [Sentence-Transformers](https://www.sbert.net/) - For text embedding and semantic search

## Getting Started

### Prerequisites

- Python 3.10+
- Docker & Docker Compose (for Qdrant)

### Local Setup

#### 1. Clone the repository
```bash
git clone <repository-url>
cd luminary-api
```

#### 2. Start Qdrant with Docker
```bash
docker-compose up -d
```
This starts Qdrant on `localhost:6333`. Verify it's running:

```bash
curl http://localhost:6333/health
```

#### 3. Create `.env` file
```bash
# .env
QDRANT_HOST=localhost
QDRANT_PORT=6333
COLLECTION_NAME=luminary_notes

EMBEDDING_MODEL=Qwen/Qwen3-Embedding-0.6B
HF_TOKEN=<your-huggingface-token>  # Optional, for private models
VECTOR_SIZE=1024

API_KEY=<your-groq-api-key>  # Required for LLM generation
GENERATIVE_MODEL=llama-3.3-70b-versatile
MAX_TOKENS=1024
TEMPERATURE=0.2

TOP_K=5
SCORE_THRESHOLD=0.45

APP_NAME=Luminary
LOG_LEVEL=INFO
```

**Get API Keys**:
- [Groq API Key](https://console.groq.com/keys)
- [HuggingFace Token](https://huggingface.co/settings/tokens) (optional)

#### 4. Install dependencies
```bash
pip install -r requirement.txt
```

**Note**: Install PyTorch/CUDA separately:

```bash
# CPU only
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# With CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### 5. Run the server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server runs at: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints
### Health Check
- **GET** `/health`
    - Check if the API and Qdrant are running
    - Returns: Status, model name, and Qdrant connection status

### Ingest
- **POST** `/api/ingest`
    - Ingest documents from a folder into the vector database
    - Request:
      ```json
      {
        "notes_folder": "/path/to/documents",
        "recreate_collection": false
      }
      ```
    - Response: Number of chunks ingested and duration in seconds

### Chat
- **POST** `/api/chat`
    - Stream a response augmented with relevant context from your knowledge base
    - Request:
      ```json
      {
        "question": "What is a mutual fund?",
        "session_id": "user-session-123"
      }
      ```
    - Response: Server-Sent Events (SSE) stream of generated text
    - Note: Session ID persists conversation history

### Session Management
- **GET** `/api/session/{session_id}`
    - Retrieve chat history for a session
    - Response: Session ID, messages, and message count

- **DELETE** `/api/session/{session_id}`
    - Clear chat history for a session
    - Response: 204 No Content

## Usage Example
```bash
# 1. Ingest documents
curl -X POST "http://localhost:8000/api/ingest" \
  -H "Content-Type: application/json" \
  -d '{"notes_folder": "./data/notes", "recreate_collection": true}'

# 2. Ask a question (streaming)
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are mutual funds?", "session_id": "session-1"}'

# 3. Get session history
curl "http://localhost:8000/api/session/session-1"

# 4. Clear session
curl -X DELETE "http://localhost:8000/api/session/session-1"
```

## Project Structure
```
luminary-api/
├── app/
│   ├── main.py              # FastAPI application setup
│   ├── config.py            # Configuration & settings
│   ├── api/
│   │   ├── routes/          # API endpoints
│   │   └── models/          # Request/response models
│   ├── core/                # Core RAG pipeline
│   │   ├── chunker.py       # Document chunking
│   │   ├── embedder.py      # Embedding generation
│   │   ├── retriever.py     # Vector search
│   │   └── generator.py     # LLM response generation
│   ├── services/            # Business logic
│   └── utils/               # Utilities & errors
├── data/
│   └── notes/               # Your knowledge base documents
├── docker-compose.yml       # Qdrant setup
├── requirement.txt          # Python dependencies
└── README.md               # This file
```

## Environment Variables Reference
| Variable           | Default                   | Description                      |
|--------------------|---------------------------|----------------------------------|
| `QDRANT_HOST`      | localhost                 | Qdrant server host               |
| `QDRANT_PORT`      | 6333                      | Qdrant server port               |
| `COLLECTION_NAME`  | luminary_notes            | Vector DB collection name        |
| `EMBEDDING_MODEL`  | Qwen/Qwen3-Embedding-0.6B | Embedding model from HuggingFace |
| `VECTOR_SIZE`      | 1024                      | Embedding vector dimension       |
| `TOP_K`            | 5                         | Number of documents to retrieve  |
| `SCORE_THRESHOLD`  | 0.45                      | Minimum similarity score         |
| `API_KEY`          | (required)                | Groq API key                     |
| `GENERATIVE_MODEL` | llama-3.3-70b-versatile   | LLM model name                   |
| `MAX_TOKENS`       | 1024                      | Max tokens in response           |
| `TEMPERATURE`      | 0.2                       | LLM creativity (0-1)             |

## License
This project is licensed under the MIT License.

### MIT License Summary
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
