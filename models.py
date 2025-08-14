# models.py
from langchain_openai import OpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embedding_model():
    """Returns a HuggingFace embedding model."""
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_llm():
    """Returns a configured LLM client."""
    # Example for LM Studio. Update for your setup (e.g., Ollama).
    return OpenAI(
        openai_api_key="not-needed",
        openai_api_base="http://10.30.15.227:1234/v1", # Use localhost
        model_name="local-model" # This is often ignored by local servers but good practice
    )