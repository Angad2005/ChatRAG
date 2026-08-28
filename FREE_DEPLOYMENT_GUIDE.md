# Free Deployment Guide for ChatRAG

This project is best deployed as a Streamlit app with a cloud-hosted OpenAI-compatible LLM. The local FastAPI summarization microservice is optional and should only be deployed separately if you specifically need summary generation.

## Best free deployment option

Use:
- Streamlit Community Cloud for the main UI (`main.py`)
- A hosted provider such as OpenAI, Together AI, Groq, or another OpenAI-compatible API for the LLM backend
- A separate Render or Railway service only for the optional summary API (`mcp_main.py`)

Recommended architecture:

```text
Browser → Streamlit app
         ├─ uploads PDF/DOCX/TXT docs
         ├─ embeds text with Hugging Face model
         └─ calls OpenAI-compatible LLM API

Optional summary service:
Browser/Streamlit → FastAPI service on Render/Railway
                       └─ generates document summary PDF/DOCX
```

## Where to deploy for free

### 1) Streamlit Community Cloud — best for the main app

Best fit for this project because the app is a Streamlit dashboard.

- Good for: `main.py`
- Free-tier suitability: Best choice for a free deployment
- Why it fits: Streamlit is the native runtime, and this project is already built as a Streamlit app
- Requirements:
  - push the repo to GitHub
  - create a new app in Streamlit Community Cloud
  - set the main file to `main.py`
  - add secrets for LLM config

Example secrets:

```toml
LLM_API_BASE = "https://api.openai.com/v1"
LLM_API_KEY = "your-api-key"
LLM_MODEL_NAME = "gpt-4o-mini"
```

Notes:
- Free Streamlit hosting has resource limits; it is not suited for running a local GPU model or large batch processing
- Use a small model and keep uploads modest
- The app must reach a public LLM endpoint; `localhost` will not work in hosted deployment

### 2) Render — best for the optional API service

Best fit for the FastAPI microservice in `mcp_main.py`.

- Good for: `/summarize-and-create-document/` and `/health`
- Free-tier suitability: Good for demos and small projects
- Recommended setup:
  - Web Service
  - Build command:

```bash
pip install -r requirements.txt
```

  - Start command:

```bash
uvicorn mcp_main:app --host 0.0.0.0 --port $PORT
```

  - Health check path:

```text
/health
```

Notes:
- Free Render services sleep when idle
- Storage is ephemeral, so generated files and caches are not durable
- The app needs a public URL, not `127.0.0.1`

### 3) Railway — workable for testing or a small full-stack deployment

Best fit when you want both UI and API hosted together or want a simple trial deployment.

- Good for: testing, demos, and combining app + API
- Free-tier suitability: often good for trials but not always permanent free hosting
- Important: check current credit and free-plan limits before relying on it

### 4) Vercel — not recommended for this project

This project is not a standard Next.js or serverless frontend app.

- Not a good match because:
  - Streamlit is not a Vercel-native runtime
  - Python long-running processes are not a good fit for Vercel serverless hosting
  - local model loading and document processing are not ideal there

Use Vercel only if you rework the app architecture substantially, such as converting the frontend into a Next.js app and moving the AI logic to a separate backend.

### 5) Cloudflare Workers — not recommended for this project

Cloudflare Workers are good for edge APIs and static frontends, but not for a Python app with:
- PyTorch
- Hugging Face embeddings
- Streamlit UI
- local file processing

They can be used only as a proxy or API front door, but not as the main runtime for this project.

## Good deployment strategy

For a free, simple setup:

1. Deploy the Streamlit app on Streamlit Community Cloud
2. Use a paid or free external OpenAI-compatible LLM provider
3. Keep the optional Python API on Render only if document-summary generation is required
4. Do not try to run GPU or local inference in free hosting unless the provider supports it

## Suggested changes before production deployment

The project currently works best in a local developer setup. For reliable cloud hosting, make these changes:

1. Remove private-network defaults
   - `models.py` currently uses a default local API base like `http://192.168.96.1:1234/v1`
   - This will not work on hosted environments
   - Replace it with a required environment variable or a clear error if unset

2. Use environment variables and secrets
   - Keep `LLM_API_BASE`, `LLM_API_KEY`, and `LLM_MODEL_NAME` in secrets or deployment environment variables
   - Do not commit real keys to the repository

3. Add explicit dependency declarations
   - Ensure `torch`, `sentence-transformers`, `langchain-text-splitters`, and `langchain-classic` are explicitly installed in `requirements.txt`
   - Do not rely on hidden transitive installs

4. Handle model cache for ephemeral hosts
   - `get_embedding_model()` expects the model to already exist in a local Hugging Face cache
   - On Render or Streamlit Cloud, the filesystem may be ephemeral or read-only
   - Consider downloading the model during the build step or using a mounted cache if supported

5. Add environment variables for the summary API
   - Add a variable like `MCP_API_URL`
   - Use it from the UI to call the Render/Railway summary service

6. Add security limits to the FastAPI API
   - Add auth or a shared secret
   - Limit upload size and request rate
   - Validate input before generating summaries

7. Plan for persistence
   - Uploaded files, vector stores, and generated documents may disappear on restarts or sleep cycles
   - If needed, move document storage to object storage or a database-backed system

## Deployment troubleshooting

### LLM connection fails
- Ensure the API base URL is public and not `localhost`
- Ensure the endpoint exposes `/v1/models` and `/v1/chat/completions`
- Confirm the model name matches the provider exactly

### Model missing
- The embedding model is cached locally and must exist before runtime
- Pre-download it once and set `HF_HOME` if needed

### Render health checks fail
- Bind Uvicorn to `0.0.0.0`
- Use `$PORT` instead of a hard-coded port
- Make sure `/health` returns a successful response

### Out-of-memory issues
- Use smaller document batches
- Use CPU-only processing
- Keep the LLM external instead of trying to run a local giant model

## Bottom line

The best free deployment for this project is:

- Streamlit Community Cloud for the main app
- public OpenAI-compatible LLM API for inference
- Render only if you need the optional summary microservice

Avoid Vercel and Cloudflare Workers for the main app unless you redesign the architecture.
