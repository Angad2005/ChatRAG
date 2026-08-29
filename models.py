from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
import requests
import os
from pathlib import Path

# Default configuration
DEFAULT_API_BASE = os.getenv("LLM_API_BASE", "http://localhost:1234/v1")
DEFAULT_API_KEY = os.getenv("LLM_API_KEY", "not-needed")
DEFAULT_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "llama-3.2-1b-instruct")

# Local cache path for pre-downloaded model
EMBEDDING_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
HF_CACHE = os.getenv("HF_HOME", os.path.expanduser("~/.cache/huggingface"))


def _find_local_model_path():
    """Find pre-downloaded model in HF cache."""
    cache_dir = Path(HF_CACHE) / "hub"
    if not cache_dir.exists():
        return None
    
    # Look for the model snapshot - match directory name exactly
    model_name_safe = EMBEDDING_MODEL_ID.replace('/', '--')
    model_dirs = list(cache_dir.glob(f"models--{model_name_safe}*"))
    
    for model_dir in model_dirs:
        snapshots = list((model_dir / "snapshots").glob("*"))
        if snapshots:
            return str(snapshots[0])
    return None


def get_embedding_model(allow_download: bool = True):
    """
    Initializes the embedding model.
    1. Checks local cache snapshot first.
    2. Falls back to downloading via Hugging Face API if allow_download is True.
    """
    import torch
    
    # Auto-detect device: CUDA > MPS > CPU
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    
    encode_kwargs = {'normalize_embeddings': False}
    model_kwargs = {'device': device}
    
    # 1. Try to load from local cache snapshot first
    local_path = _find_local_model_path()
    if local_path:
        return HuggingFaceEmbeddings(
            model_name=local_path,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
    
    # 2. Fallback to Hugging Face API download if enabled
    if allow_download:
        try:
            return HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL_ID,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )
        except Exception as e:
            raise RuntimeError(f"Failed to fetch model from Hugging Face Hub: {e}") from e

    # 3. If offline/cache-only mode failed
    raise RuntimeError(
        f"Embedding model not found in local cache ({HF_CACHE}).\n"
        f"Pre-download it first or enable online download."
    )


def get_llm(api_base=None, api_key=None, model_name=None) -> ChatOpenAI:
    """Initializes the LLM with configurable parameters."""
    return ChatOpenAI(
        api_key=api_key or DEFAULT_API_KEY,
        base_url=api_base or DEFAULT_API_BASE,
        model=model_name or DEFAULT_MODEL_NAME,
    )


def verify_llm_model_availability(llm_client: ChatOpenAI):
    """Verifies that the specified model is available at the API endpoint."""
    model_to_check = llm_client.model_name
    api_base = getattr(llm_client, 'base_url', None) or getattr(llm_client, 'openai_api_base', None)
    
    if not api_base:
        raise ValueError("Could not determine API base URL from LLM client.")

    api_base = str(api_base).rstrip("/")
    models_url = f"{api_base}/models"
    
    try:
        response = requests.get(models_url, timeout=10)
        response.raise_for_status()
        
        available_models = response.json().get("data", [])
        available_model_ids = [model.get("id") for model in available_models]
        
        if model_to_check not in available_model_ids:
            error_message = (
                f"Model '{model_to_check}' is not available at the endpoint.\n"
                f"Available models are: {available_model_ids}"
            )
            raise ValueError(error_message)
            
    except requests.exceptions.RequestException as e:
        raise ConnectionError(
            f"Failed to connect to the LLM API at {models_url}. "
            "Please ensure the server is running and accessible."
        ) from e
    except ValueError:
        raise