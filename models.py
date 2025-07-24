# models.py
from langchain.llms import OpenAI
from langchain.embeddings import HuggingFaceEmbeddings

def get_embedding_model():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_llm():
    return OpenAI(
        openai_api_key="not-needed",
        openai_api_base="http://172.16.0.2:1234/v1",
        model_name="lmstudio-ai/your-model-name"
    )