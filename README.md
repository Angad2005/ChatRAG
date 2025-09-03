# 🚀 ChatRAG ( Chatbot AI Agent & Knowledge Base Injector)

> LLM-powered tool for working with your datafiles and other data files locally on your own system or server.

> Also make your LLM and other models more knowledgeable using this data injector.

## 📌 Description
This project uses Python for both front-end and back-end, connecting to your LLM for easy access. For ease of access, this project requires an API or another endpoint like Ollama, LM Studio, etc.
- Users can access their personal private files on their own local systems using LLMs for fast understanding and advanced reasoning.
- Can run on any LLM that your system supports (results may vary from model to model).
- Read the requirements file to see technologies used.

## Demo
https://drive.google.com/file/d/1DkBTtHKwj6ADI5ju6SYtKZYwiiBjwpsX/view?usp=sharing


## 🌟 Features
- ✨ Real-time data processing, understanding, and advanced reasoning.
- 🚀 Multi-platform support.
- 🔐 Full security as everything happens locally.
- 📊 Customizable LLMs data and can be used for other file types and files.

## 📦 Installation
- Recommended to run on WSL (Windows Subsystem for Linux) or a Linux distro for the best CORS (Cross-Origin Resource Sharing) experience, as Windows CORS may be limited depending on user customization and settings.

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

# Run tool
streamlit run main.py

# Optional:
# Change API endpoints in models.py file
# OpenAI for direct API integration
def get_llm():
    return OpenAI(
        openai_api_key="not-needed",
        openai_api_base="http://192.168.29.31:1234/v1",
        model_name="lmstudio-ai/your-model-name"
    )
```

## Example of LLM Endpoints

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
OLLAMA_MODEL=llama3  # Replace with your desired model name (e.g., "mistral", "phi3")  
```

## 🧪 Usage
```bash
# Start the app
streamlit run main.py
```

## ⚙️ Configuration

### File Upload Settings
Edit `main.py` to customize file types:

```python
# File upload (supports multiple formats)
uploaded_files = st.file_uploader(
    "Upload Documents",
    type=["pdf", "docx", "txt", "csv", "xlsx"],  # Add/remove formats here
    accept_multiple_files=True
)
```

### LLM Backend Configuration
Update `models.py` to set your LLM backend.

#### LM Studio Example
```python
def get_llm():
    return OpenAI(
        openai_api_key="EMPTY",  # Use "EMPTY" if authentication is disabled
        openai_api_base="http://localhost:1234/v1",
        model_name="lmstudio-ai/your-model-name"
    )
```

#### Ollama Example
```python
def get_llm():
    return OpenAI(
        openai_api_key="EMPTY",
        openai_api_base="http://localhost:11434/v1",
        model_name="llama3"  # Replace with your desired model
    )
```

## 🧩 Supported LLM Backends

### LM Studio
```bash
LLM_BACKEND=lmstudio  
LMSTUDIO_API_KEY=your_lmstudio_api_key  # Usually "EMPTY"
LMSTUDIO_ENDPOINT=http://localhost:1234/v1  
```

### Ollama
```bash
LLM_BACKEND=ollama  
OLLAMA_HOST=http://localhost:11434  
OLLAMA_MODEL=llama3  # Replace with your desired model (e.g., "mistral", "phi3")
```

## 🤝 Contributing
Contributions are welcome! Whether you're fixing bugs, improving documentation, or adding new features, follow these guidelines:

1. **Fork the Repository**  
   Click the "Fork" button at the top-right of the GitHub page.

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Follow PEP8 style guidelines.
   - Write clear, descriptive commit messages.
   - Test your changes thoroughly.

4. **Submit a Pull Request**
   Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
   Open a pull request on the original repository with:
   - A clear title and description
   - Screenshots (if applicable)
   - Relevant issue number (if fixing a bug)

5. **Code of Conduct**  
   We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). Please report any unacceptable behavior.

6. **Reporting Issues**  
   - Check the GitHub Issues tab first to avoid duplicates.
   - Include:
     - Detailed steps to reproduce
     - Expected vs. actual behavior
     - Screenshots/logs (if relevant)

## 📄 License
This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
