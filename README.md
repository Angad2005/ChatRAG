# 🚀 ChatRAG (Chatbot AI Agent & Knowledge Base Injector)

> LLM-powered tool for working with your data files locally on your own system or server. Makes your LLM more knowledgeable using document injection.

## 📌 Description

This project uses Python for both front-end (Streamlit) and back-end, connecting to any OpenAI-compatible LLM endpoint (LM Studio, vLLM, Ollama, NVIDIA NIM, OpenAI, etc.).

- Chat with your personal private files using LLMs for fast understanding and advanced reasoning
- Runs on any OpenAI-compatible LLM backend (results vary by model)
- GPU-accelerated embeddings with auto CUDA/MPS/CPU detection
- No runtime downloads — models pre-cached locally

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Angad2005/ChatPDF.git
   cd ChatPDF
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   python3 -m venv van1
   source van1/bin/activate      # Linux/Mac
   # .\van1\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install PyTorch with CUDA support** (for GPU embeddings)
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cu121
   ```

5. **Pre-download the embedding model** (one-time, requires internet)
   ```bash
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
   ```
   This caches `~90 MB` to `~/.cache/huggingface/hub/`. Set `HF_HOME` to change cache location.

## 🐳 Usage

### Step 1: Start the MCP Summarization Service (optional, for summary generation)
```bash
# In a separate terminal:
uvicorn mcp_main:app --host 127.0.0.1 --port 8001
```

### Step 2: Start the Streamlit Application
```bash
# Disable file watcher to avoid transformers import errors
STREAMLIT_SERVER_FILE_WATCHER_TYPE=none streamlit run main.py
```
The application opens at `http://localhost:8501`.

### Step 3: Use the Application

1. **Configure LLM** (Sidebar → 🤖 LLM Settings):
   - **API Base URL**: `http://localhost:1234/v1` (LM Studio), `http://localhost:8000/v1` (vLLM), `http://localhost:11434/v1` (Ollama), `https://integrate.api.nvidia.com/v1` (NVIDIA NIM)
   - **API Key**: `not-needed` (local) or your API key (cloud)
   - **Model Name**: Exact model ID from your server (e.g., `llama-3.2-1b-instruct`, `meta/llama-3.1-8b-instruct`)
   - Click **💾 Save & Connect** — tests `/v1/models` endpoint

2. **Load Embedding Model** (Sidebar → 📦 Embedding Model):
   - Click **📂 Load from Cache** — loads `sentence-transformers/all-MiniLM-L6-v2` from local cache
   - Auto-detects GPU (CUDA/MPS) with CPU fallback
   - Shows cache path and device in UI

3. **Upload Documents**: PDF, DOCX, TXT via sidebar file uploader

4. **Ask Questions**: Chat with your documents in the main area

5. **Generate Summaries** (requires MCP service):
   - Select format (PDF/DOCX)
   - Click **Create Summary Document**
   - Download the result

6. **Reset**: **🗑️ Clear Chat** clears history and vector store

## ⚙️ Configuration

### LLM Backend (via Sidebar GUI — no code edits needed)

| Backend | API Base URL | API Key | Example Model Name |
|---------|--------------|---------|-------------------|
| LM Studio | `http://localhost:1234/v1` | `not-needed` | `llama-3.2-1b-instruct` |
| vLLM | `http://localhost:8000/v1` | `not-needed` | `meta-llama/Llama-3.1-8B-Instruct` |
| Ollama | `http://localhost:11434/v1` | `not-needed` | `llama3.1:8b` |
| NVIDIA NIM (cloud) | `https://integrate.api.nvidia.com/v1` | your NVIDIA API key | `meta/llama-3.1-8b-instruct` |
| NVIDIA NIM (local) | `http://localhost:8000/v1` | `not-needed` | `meta/llama-3.1-8b-instruct` |
| OpenAI | `https://api.openai.com/v1` | `sk-...` | `gpt-4o-mini` |
| Together AI | `https://api.together.xyz/v1` | your key | `meta-llama/Llama-3.1-8B-Instruct-Turbo` |

The server must implement:
- `GET /v1/models` — returns `{ "data": [{ "id": "model-name" }, ...] }`
- `POST /v1/chat/completions` — OpenAI chat completion format

### Environment Variables (Optional)
```bash
# Embedding model cache location
export HF_HOME=/path/to/cache

# Hugging Face mirror (if blocked)
export HF_ENDPOINT=https://hf-mirror.com

# LLM defaults (overridden by sidebar)
export LLM_API_BASE=http://localhost:1234/v1
export LLM_API_KEY=not-needed
export LLM_MODEL_NAME=llama-3.2-1b-instruct
```

## 📄 File Format Support
- PDF (.pdf)
- Word Document (.docx)
- Plain Text (.txt)

## 🔧 Troubleshooting

### Streamlit file watcher errors (transformers/torch import)
**Fixed by:** `STREAMLIT_SERVER_FILE_WATCHER_TYPE=none streamlit run main.py`

### Embedding model not found in cache
Run the pre-download command from Installation step 5. The UI shows the cache path it's checking.

### GPU not used
- Verify CUDA: `python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"`
- Reinstall PyTorch with CUDA: `pip install torch --index-url https://download.pytorch.org/whl/cu121`
- The app auto-detects CUDA → MPS → CPU

### LLM connection fails
- Test endpoint: `curl http://localhost:1234/v1/models`
- Check model name matches exactly what `/v1/models` returns
- For LM Studio: Enable "OpenAI Compatible Server" in Settings → Developer

### SSL/Cert errors downloading model
```bash
pip install --upgrade certifi
# Or use mirror:
HF_ENDPOINT=https://hf-mirror.com python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

## 📝 License
MIT License — see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments
- [Streamlit](https://streamlit.io/)
- [LangChain](https://www.langchain.com/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
- [sentence-transformers](https://www.sbert.net/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [PyTorch](https://pytorch.org/)