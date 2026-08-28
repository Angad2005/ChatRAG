---
title: ChatRAG - AI Knowledge Base Agent
emoji: 
colorFrom: blue
colorTo: purple
sdk: gradio
app_file: app.py
pinned: false
license: mit
short_description: Chat with your PDFs, DOCX, and TXT files using RAG and any OpenAI-compatible LLM.
tags:
- rag
- llm
- gradio
- langchain
- document-chat
- pdf
---

# 🚀 ChatRAG (Chatbot AI Agent & Knowledge Base Injector)

<div align="center">
  <img src="https://img.shields.io/badge/Gradio-F97316?style=for-the-badge&logo=gradio&logoColor=white" alt="Gradio">
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black" alt="HuggingFace">
</div>

> **LLM-powered tool for working with your data files.** Makes your LLM more knowledgeable using document injection and Retrieval-Augmented Generation (RAG). Built with Gradio for a modern, responsive interface.

## 🌟 Features

- 📄 **Multi-Format Support**: Upload PDF, DOCX, and TXT files.
-  **Smart RAG**: Uses FAISS vector store and SentenceTransformers for accurate retrieval.
- 🔌 **Flexible LLM Backend**: Connect to **any** OpenAI-compatible endpoint:
  - ☁️ Cloud APIs: OpenAI, NVIDIA NIM, Together AI, Groq.
  - 🏠 Local Servers: Ollama, LM Studio, vLLM (requires network tunneling like ngrok).
- ⚡ **GPU Accelerated**: Auto-detects CUDA/MPS for faster embedding generation.
- 🔒 **Private**: Your documents are processed locally in session memory.

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

> **⚠️ Note for Hugging Face Spaces Users:** This Space runs in a cloud container. It **cannot** directly access `localhost` on your personal computer. To use local models like Ollama or LM Studio, you must expose them via a secure tunnel (e.g., ngrok, cloudflare) or use a Cloud API provider listed above.

### 2. Load Embedding Model
Click **📂 Load from Cache** in the sidebar. This loads the lightweight `all-MiniLM-L6-v2` model for creating vector embeddings of your documents.

### 3. Upload & Chat
1. Upload your `.pdf`, `.docx`, or `.txt` files using the file uploader.
2. Click **🔧 Process Documents** to index them into the vector store.
3. Ask questions about your documents in the chat box!

## 🛠️ Technical Details

- **Frontend**: Gradio
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

# Optional: Install PyTorch with CUDA support for GPU embeddings
# pip install --upgrade torch --index-url https://download.pytorch.org/whl/cu121

# Run the Gradio app
python app.py