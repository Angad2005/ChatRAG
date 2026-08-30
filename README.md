# Deployment
https://angad2005-chatrag-main-sirokb.streamlit.app/

# 🚀 ChatRAG (Chatbot AI Agent & Knowledge Base Injector)

<div align="center">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black" alt="HuggingFace">
</div>

> **LLM-powered tool for working with your data files.** Makes your LLM more knowledgeable using document injection and Retrieval-Augmented Generation (RAG).

## 🌟 Features

- 📄 **Multi-Format Support**: Upload PDF, DOCX, and TXT files.
- 🧠 **Smart RAG**: Uses FAISS vector store and SentenceTransformers for accurate retrieval.
- 🔌 **Flexible LLM Backend**: Connect to **any** OpenAI-compatible endpoint:
  - ☁️ Cloud APIs: OpenAI, NVIDIA NIM, Together AI, Groq.
  - 🏠 Local Servers: Ollama, LM Studio, vLLM (if running on same network/machine).
- ⚡ **GPU Accelerated**: Auto-detects CUDA/MPS for faster embedding generation.
- 🔒 **Private**: Your documents are processed locally in the session memory.

## 🚀 Quick Start

### 1. Configure LLM Connection
In the sidebar (**🤖 LLM Settings**), enter your provider details:

| Provider | API Base URL | API Key | Example Model |
|----------|--------------|---------|---------------|
| **OpenAI** | `https://api.openai.com/v1` | `sk-...` | `gpt-4o-mini` |
| **NVIDIA NIM** | `https://integrate.api.nvidia.com/v1` | `nvapi-...` | `meta/llama-3.1-8b-instruct` |
| **Groq** | `https://api.groq.com/openai/v1` | `gsk_...` | `llama3-8b-8192` |
| **Ollama** (Local) | `http://localhost:11434/v1` | `not-needed` | `llama3.1` |
| **LM Studio** (Local) | `http://localhost:1234/v1` | `not-needed` | `local-model` |

> **Note for Hugging Face Spaces Users:** Since this Space runs in the cloud, it cannot connect to `localhost` on your computer. To use local models like Ollama/LM Studio, you must expose them via a tunnel (like ngrok) or use a Cloud API provider listed above.

### 2. Load Embedding Model
Click **📂 Load from Cache** in the sidebar. This loads the lightweight `all-MiniLM-L6-v2` model for creating vector embeddings of your documents.

### 3. Upload & Chat
1. Upload your `.pdf`, `.docx`, or `.txt` files.
2. Wait for the "Processing Complete" message.
3. Ask questions about your documents in the chat box!

## 🛠️ Technical Details

- **Frontend**: Streamlit
- **Backend**: Python / LangChain
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`)
- **Document Loaders**: PyPDF, python-docx

## 📦 Local Installation

If you want to run this locally with full GPU support:

```bash
git clone https://github.com/Angad2005/ChatRAG.git
cd ChatRAG

# Create virtual environment
python -m venv van1
source van1/bin/activate  # Linux/Mac
# .\van1\Scripts\activate # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
STREAMLIT_SERVER_FILE_WATCHER_TYPE=none streamlit run main.py
