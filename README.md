# 🚀 ChatPDf

> LLM powerwed tool for working your pdfs and other data files locally on your own system or server.

## 📌 Description
This project works with python as base front-end as well as back-end. Python also connects it to your LLM for easy access. For ease of access this project requires an API or another endpoint like Ollama, Lm studio,....etc.
- Users can now access their personal private files on thier own local systems using LLMs for fast understanding and advance reasoning.
- Can run on any LLM which your system supports(results may vary from model to model).
- Read requirements file to see technologies used.

## 🌟 Features
- ✨ Real-time data processing, understanding and advance reasoning.
- 🚀 Multi-platform support.
- 🔐 Full security as everything happens locally.
- 📊 Customizable LLMs data and can be used for other file types and files.

## 📦 Installation
```bash
# Clone the repository
git clone https://github.com/Angad2005/ChatPDF.git

# Navigate to the directory
cd ChatPDF

# Optional: Create and activate a virtual environment
python3 -m venv env          # Create virtual environment
source env/bin/activate      # On Windows use: .\env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

#Run tool
streamlit run main.py

# Optional: Change file type for advance data processing in code
# File upload
    pdf_docs = st.file_uploader(
        "Upload PDF(s)",
        type="pdf",
        accept_multiple_files=True
    )

# Change API endpoints in models.py file
# OpenAI for direct API integration
def get_llm():
    return OpenAI(
        openai_api_key="not-needed",
        openai_api_base="http://192.168.29.31:1234/v1",
        model_name="lmstudio-ai/your-model-name"
    )
```

## Exmple of LLM endpoints

## LM studio
LLM_BACKEND=lmstudio  
LMSTUDIO_API_KEY=your_lmstudio_api_key  # Usually "EMPTY" if authentication is disabled  
LMSTUDIO_ENDPOINT=http://localhost:1234/v1  

## Ollama
LLM_BACKEND=ollama  
OLLAMA_HOST=http://localhost:11434  
OLLAMA_MODEL=llama3  # Replace with your desired model name (e.g., "mistral", "phi3")  

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
