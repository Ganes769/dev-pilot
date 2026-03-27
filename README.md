# DevPilot

DevPilot is a FastAPI-based repository assistant that scans source files, splits them into chunks, generates embeddings, stores those vectors in Qdrant, and answers natural-language questions about the indexed codebase with Ollama.

It also includes a small CLI for indexing a repository and asking questions from the terminal.

## What It Does

- Scans a repository for supported files
- Reads file contents safely with UTF-8 fallback handling
- Splits file contents into overlapping text chunks
- Embeds chunks with `sentence-transformers`
- Stores vectors and chunk metadata in Qdrant
- Retrieves the most relevant chunks for a question
- Sends retrieved context to an Ollama model to generate an answer
- Returns answer text together with source file references

## Tech Stack

- FastAPI
- Pydantic
- Qdrant
- sentence-transformers
- Ollama
- Typer
- Rich

## Project Structure

```text
dev-pilot/
├── app/
│   ├── api/routes/
│   │   ├── ask.py
│   │   ├── chunck.py
│   │   ├── embed.py
│   │   ├── repo.py
│   │   ├── search.py
│   │   └── vector.py
│   ├── db/
│   │   └── qdrant_client.py
│   ├── models/
│   │   └── schema.py
│   ├── services/
│   │   ├── chuncker.py
│   │   ├── embedding_service.py
│   │   ├── extra_context.py
│   │   ├── file_reader.py
│   │   ├── llm_service.py
│   │   ├── repo_scanner.py
│   │   └── vector_store.py
│   └── main.py
├── cli.py
├── requirements.txt
└── README.md
```

## How The System Works

### 1. Repository scanning

`app/services/repo_scanner.py` walks the target repository and keeps files whose extensions are currently supported:

- `.py`
- `.md`
- `.yaml`
- `.yml`
- `.txt`

Ignored directories include:

- `.git`
- `venv`
- `.venv`
- `__pycache__`
- `.pytest_cache`
- `node_modules`

### 2. File reading

`app/services/file_reader.py` reads each file as UTF-8. If decoding fails, it retries with `errors="ignore"` so indexing can continue instead of crashing on partially invalid text.

### 3. Chunking

`app/services/chuncker.py` splits text into overlapping chunks. This helps preserve context between adjacent segments and improves semantic retrieval.

Default values:

- `chunk_size = 1000`
- `overlap = 100`

### 4. Embedding

`app/services/embedding_service.py` uses the model:

```text
all-MiniLM-L6-v2
```

This produces 384-dimensional vectors, which matches the Qdrant collection configuration in `app/services/vector_store.py`.

### 5. Vector storage

Vectors are stored in the Qdrant collection:

```text
repo_chunks
```

Each stored point contains:

- `id`
- `vector`
- `file_path`
- `chunk_index`
- `text`

### 6. Question answering

When you call `POST /ask`:

1. The question is embedded.
2. Qdrant returns the closest matching chunks.
3. Matches below the similarity threshold are skipped.
4. The remaining chunks are stitched into a single context block.
5. The context is sent to Ollama through `app/services/llm_service.py`.
6. The API returns an answer and a list of source chunks.

## Prerequisites

Before running DevPilot, make sure you have:

- Python 3.10 or newer
- Qdrant running on `localhost:6333`
- Ollama installed locally
- The Ollama model `gemma3` pulled locally

## Installation

### 1. Clone the project

```bash
git clone <your-repo-url>
cd dev-pilot
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Note: on the first run, `sentence-transformers` may download the embedding model.

## Running Dependencies

### Start Qdrant

If you use Docker:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Start Ollama and pull the model

```bash
ollama pull gemma3
```

## Running The API

From the project root:

```bash
python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{ "status": "ok" }
```

FastAPI docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redocs`

## Environment Variables

`app/main.py` loads environment variables from a local `.env` file if present.

Supported variables:

### `DEVPILOT_URL`

Used by the CLI to choose which API base URL to call.

Example:

```bash
export DEVPILOT_URL=http://127.0.0.1:8000
```

### `DEVPILOT_EXTRA_CONTEXT`

Inline text appended to the LLM prompt for identity, greetings, product description, or other non-code context.

Example:

```env
DEVPILOT_EXTRA_CONTEXT=You are DevPilot, a repository assistant built with FastAPI, Qdrant, and Ollama.
```

### `DEVPILOT_EXTRA_CONTEXT_FILE`

Path to a UTF-8 file containing extra context. If this is set and the file exists, it takes precedence over `DEVPILOT_EXTRA_CONTEXT`.

Example:

```env
DEVPILOT_EXTRA_CONTEXT_FILE=/absolute/path/to/context.txt
```

## CLI Usage

The CLI lives in `cli.py`.

Show help:

```bash
python3 -m cli --help
```

### Index a repository

```bash
python3 -m cli index /absolute/path/to/repository
```

Optional parameters:

- `chunk_size`
- `overlap`

Example:

```bash
python3 -m cli index /absolute/path/to/repository --chunk-size 1200 --overlap 150
```

### Ask a question

```bash
python3 -m cli ask "How does the ask endpoint work?"
```

With extra one-off context:

```bash
python3 -m cli ask "Who are you?" --extra "Say you are DevPilot and briefly explain your purpose."
```

## API Endpoints

### `GET /health`

Simple health check endpoint.

### `POST /repos/index`

Scans the repository and returns the list of indexable files.

Example request:

```json
{
  "repo_path": "/absolute/path/to/repository"
}
```

### `POST /repo/chunck`

Scans the repository, chunks each file, and returns a preview of chunked content.

Example request:

```json
{
  "repo_path": "/absolute/path/to/repository",
  "chunck_size": 1000,
  "overlap": 100
}
```

### `POST /vector/setup`

Creates the Qdrant collection if it does not already exist.

### `POST /repos/embed`

Scans, reads, chunks, embeds, and stores repository content in Qdrant.

Example request:

```json
{
  "repo_path": "/absolute/path/to/repository",
  "chunk_size": 1000,
  "overlap": 100
}
```

Example response:

```json
{
  "repo_name": "my-project",
  "total_files": 24,
  "total_chunks": 138,
  "vectors_stored": 138,
  "collection": "repo_chunks"
}
```

### `POST /search`

Runs semantic search against stored chunks and returns matching snippets.

Example request:

```json
{
  "query": "How is the repository scanned?",
  "limit": 5
}
```

### `POST /ask`

Answers a natural-language question using retrieved code chunks plus optional extra context.

Example request:

```json
{
  "question": "How does file reading handle decoding issues?",
  "limit": 3
}
```

Example request with extra context:

```json
{
  "question": "Who are you?",
  "limit": 3,
  "extra_context": "You are DevPilot, a backend repository assistant."
}
```

## Example Workflow

1. Start Qdrant.
2. Start Ollama and pull `gemma3`.
3. Start the FastAPI server.
4. Index a repository with the CLI or `POST /repos/embed`.
5. Ask questions with `python3 -m cli ask ...` or `POST /ask`.

## Important Notes

- The current Ollama model is hardcoded as `gemma3` in `app/services/llm_service.py`.
- Qdrant is currently hardcoded to `localhost:6333` in `app/db/qdrant_client.py`.
- The project uses the spelling `chunck` in several file names, route names, and schema fields. The README documents the current API as implemented.
- The `/ask` and `/search` routes filter out matches with scores below `0.4`.
- If no relevant chunks are found, `/ask` returns a fallback response unless extra context is available.

## Known Limitations

- There is no persistence/config layer for Qdrant host, port, collection name, or model choice yet.
- Re-indexing appends points through the current embed flow rather than explicitly clearing older collection contents first.
- Supported file types are intentionally limited.
- The current chunk preview route uses `chunck` naming to match the codebase, which may be confusing for API consumers.

## Future Improvements

- Add configuration through environment variables
- Add tests for routes and services
- Support more file types
- Support collection reset or per-repository namespaces
- Improve chunking to be syntax-aware for code files
- Standardize naming from `chunck` to `chunk`

## License

Add your preferred license information here.
