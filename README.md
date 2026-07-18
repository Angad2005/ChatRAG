# 🚀 ChatRAG (Chatbot AI Agent & Knowledge Base Injector)

> LLM-powered tool for working with your data files locally on your own system or server. Also makes your LLM and other models more knowledgeable using this data injector.

## 📌 Description

This project uses Python for both front-end and back-end, connecting to your LLM for easy access. For ease of access, this project requires an API or another endpoint like Ollama, LM Studio, etc.

- Users can access their personal private files on their own local systems using LLMs for fast understanding and advanced reasoning.
- Can run on any LLM that your system supports (results may vary from model to model).
- Read the requirements file to see technologies used.

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Angad2005/ChatPDF.git
   cd ChatPDF
   ```

2. **Optional: Create and activate a virtual environment**
   ```bash
   python3 -m venv env          # Create virtual environment
   source env/bin/activate      # On Windows use: .\env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install additional dependencies for the MCP service**
   ```bash
   pip install uvicorn
   ```

## 🐳 Usage

### Step 1: Start the MCP Summarization Service (Required for summary generation)
```bash
# In a separate terminal window/tab:
uvicorn mcp_main:app --host 127.0.0.1 --port 8001
```
You should see output indicating the server is running, including:
```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
```

### Step 2: Start the Streamlit Application
```bash
# In another terminal window/tab (after activating the virtual environment if used):
streamlit run main.py
```
The application will open in your default web browser at http://localhost:8501.

### Step 3: Use the Application
1. **Upload Documents**: Use the file uploader in the sidebar to add PDF, DOCX, TXT, CSV, or XLSX files.
2. **Process Documents**: After uploading, click "Process" (automatic) or wait for the processing spinner.
3. **Ask Questions**: Once processed, ask questions about your documents in the chat input.
4. **Generate Summaries**: 
   - In the sidebar, select "Summary Format" (PDF or DOCX)
   - Click "Create Summary Document"
   - Wait for the confirmation, then click "Download Summary" to get your summarized document.
5. **Reset**: Click "Delete All Documents & Reset" to clear the workspace and start over.

## ⚙️ Configuration

### LLM Backend Configuration
Edit `models.py` to set your LLM backend:

#### LM Studio Example
```python
def get_llm():
    return OpenAI(
        openai_api_key="not-needed",
        openai_api_base="http://localhost:1234/v1",
        model_name="lmstudio-ai/your-model-name"
    )
```

#### Ollama Example
```python
def get_llm():
    return OpenAI(
        openai_api_key="not-needed",
        openai_api_base="http://localhost:11434/v1",
        model_name="llama3"
    )
```

### File Upload Settings
Edit `main.py` to customize file types:
```python
uploaded_files = st.file_uploader(
    "Upload Documents",
    type=["pdf", "docx", "txt", "csv", "xlsx"],  # Add/remove formats here
    accept_multiple_files=True
)
```

## 🧩 Supported LLM Backends

### LM Studio
```bash
LLM_BACKEND=lmstudio
LMSTUDIO_API_KEY=your_lmstudio_api_key  # Usually "EMPTY" if authentication is disabled
LMSTUDIO_ENDPOINT=http://localhost:1234/v1
```

### Ollama
```bash
LLM_BACKEND=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3  # Replace with your desired model (e.g., "mistral", "phi3")
```

## 📄 File Format Support
- PDF (.pdf)
- Word Document (.docx)
- Plain Text (.txt)
- CSV (.csv)
- Excel (.xlsx)

## 🔧 Troubleshooting

### MCP Service Not Running
- Ensure the MCP service is running on `http://127.0.0.1:8001`
- Check its health with: `curl http://127.0.0.1:8001/health`
- Should return `{"status":"ok"}`

### Model Loading Issues
- The MCP service uses `t5-small` for summarization. Ensure you have internet access to download the model on first run.
- If you encounter rate limits, consider setting a Hugging Face token (`HF_TOKEN` environment variable).

### Streamlit Issues
- Make sure you're running `streamlit run main.py` from the project directory.
- If the browser doesn't open automatically, navigate to `http://localhost:8501`.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments
- [Streamlit](https://streamlit.io/)
- [LangChain](https://www.langchain.com/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
- [FastAPI](https://fastapi.tiangolo.com/)