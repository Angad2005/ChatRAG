# models.py
from langchain_community.llms import OpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
import requests
import os

# Default configuration (can be overridden by environment variables or GUI)
DEFAULT_API_BASE = os.getenv("LLM_API_BASE", "http://192.168.96.1:1234/v1")
DEFAULT_API_KEY = os.getenv("LLM_API_KEY", "not-needed")
DEFAULT_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "llama-3.2-1b-instruct")

def get_embedding_model():
    """Initializes the embedding model, with GPU fallback to CPU."""
    import torch
    
    # Auto-detect device: CUDA > MPS > CPU
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    encode_kwargs = {'normalize_embeddings': False}
    
    # Try primary device
    try:
        model_kwargs = {'device': device}
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
    except Exception as e:
        # Fallback to CPU if GPU fails
        if device != "cpu":
            try:
                model_kwargs = {'device': 'cpu'}
                return HuggingFaceEmbeddings(
                    model_name=model_name,
                    model_kwargs=model_kwargs,
                    encode_kwargs=encode_kwargs
                )
            except Exception:
                pass
        raise ConnectionError(
            "Failed to download or load embedding model. "
            "Please check internet connection to huggingface.co."
        ) from e

def get_llm(api_base=None, api_key=None, model_name=None):
    """Initializes the LLM with configurable parameters."""
    return OpenAI(
        openai_api_key=api_key or DEFAULT_API_KEY,
        openai_api_base=api_base or DEFAULT_API_BASE,
        model_name=model_name or DEFAULT_MODEL_NAME,
    )

def verify_llm_model_availability(llm_client: OpenAI):
    """
    Verifies that the specified model is available at the API endpoint.
    Raises an exception if the model is not found or the API is unreachable.
    """
    model_to_check = llm_client.model_name
    api_base = llm_client.openai_api_base
    
    # Construct the correct URL for the /models endpoint
    models_url = api_base.replace("/v1", "") + "/v1/models"
    
    try:
        response = requests.get(models_url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        available_models = response.json().get("data", [])
        available_model_ids = [model.get("id") for model in available_models]
        
        if model_to_check not in available_model_ids:
            # Provide a helpful error message if the model is not in the list
            error_message = (
                f"Model '{model_to_check}' is not available at the endpoint.\n"
                f"Available models are: {available_model_ids}"
            )
            raise ValueError(error_message)
            
    except requests.exceptions.RequestException as e:
        # Catch any network errors (connection, timeout, etc.)
        raise ConnectionError(
            f"Failed to connect to the LLM API at {models_url}. "
            "Please ensure the server is running and accessible."
        ) from e
    except Exception as e:
        # Re-raise other exceptions with context
        raise RuntimeError(f"An unexpected error occurred while verifying the LLM model: {e}") from e