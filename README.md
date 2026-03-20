# DevPilot

FastAPI backend that embeds a repository into Qdrant and answers questions with retrieval + a local LLM (Ollama). A small **CLI** talks to the API for indexing and `ask`.

## Prerequisites

- **Python 3.10+** (use `python3` if `python` is not available)
- **Qdrant** at `localhost:6333` (see [Qdrant quickstart](https://qdrant.tech/documentation/quick-start/))
- **Ollama** with the model configured in `app/services/llm_service.py` (default: `gemma3`)

## 1. Clone and virtual environment

```bash
cd dev-pilot
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

On first run, **sentence-transformers** may download the embedding model (`all-MiniLM-L6-v2`).

## 2. Start Qdrant

Example with Docker:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

## 3. Ollama

Install [Ollama](https://ollama.com/), start it, then pull the chat model (match `MODEL_NAME` in `app/services/llm_service.py`):

```bash
ollama pull gemma3
```

## 4. Start the API

From the project root (with `.venv` activated):

```bash
python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) → `{"status":"ok"}`.

Environment variables are loaded from a **`.env`** file in the project root (if present) thanks to `load_dotenv()` in `app/main.py`.

## Extra context (greetings, identity, “how are you”, etc.)

By default, `/ask` is **code-grounded**: if nothing relevant is retrieved from the vector DB, you get a short “no evidence” message. To let the model answer **meta questions** (who you are, how you are, product blurb) **without** repo hits, add **optional context** in any of these ways:

1. **`.env`** (recommended for local dev)

   ```env
   DEVPILOT_EXTRA_CONTEXT=You are DevPilot. For greetings like "how are you", reply briefly that you're ready to help explore the indexed codebase. You were built with FastAPI, Qdrant, and Ollama.
   ```

2. **File** (easier for long text). If this path exists, it **replaces** the env string (not merged):

   ```env
   DEVPILOT_EXTRA_CONTEXT_FILE=/absolute/path/to/context.txt
   ```

3. **Per request** — JSON body field `extra_context` on `POST /ask` (appended after the server-loaded text).

4. **CLI** — one-off text:

   ```bash
   python3 -m cli ask how are you --extra "Say you're DevPilot and doing well; offer to help with the repo."
   ```

When **any** of the above is set, the model still uses **retrieved code** for repo questions; the extra block covers identity and small talk. Implementation: `app/services/extra_context.py`, `app/services/llm_service.py`, `app/api/routes/ask.py`.

## 5. Initialize and use the CLI

The CLI is **`cli.py`**. Run it as a module from the repo root so imports resolve if you extend the package later.

```bash
python3 -m cli --help
```

### Index a repository

Embeds files into Qdrant (path should be absolute or correct relative to where the API process resolves paths):

```bash
python3 -m cli index /absolute/path/to/your/repo
```

Options: `--chunk-size`, `--overlap` (see `--help`).

### Ask a question

Always include the **`ask`** subcommand, then the full question (all words are joined):

```bash
python3 -m cli ask how does the embed route work
```

For punctuation that zsh treats specially (e.g. `?`), quote the question:

```bash
python3 -m cli ask "where is the chunk API defined?"
```

Optional: `--limit` (number of chunks to retrieve).

### Point the CLI at another API URL

```bash
export DEVPILOT_URL=http://127.0.0.1:8000
python3 -m cli ask your question here
```

## Typical flow

1. Qdrant running  
2. Ollama running with the expected model  
3. `uvicorn` running  
4. `python3 -m cli index <repo>`  
5. `python3 -m cli ask <natural language question>`

## Project layout (short)

| Piece | Role |
|--------|------|
| `app/main.py` | FastAPI app |
| `app/api/routes/embed.py` | `POST /repos/embed` |
| `app/api/routes/ask.py` | `POST /ask` |
| `cli.py` | Typer CLI → HTTP client |
