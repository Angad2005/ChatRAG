import os
import tempfile
from pathlib import Path
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from models import (
    get_embedding_model,
    get_llm,
    verify_llm_model_availability,
    DEFAULT_API_BASE,
    DEFAULT_API_KEY,
    DEFAULT_MODEL_NAME,
    EMBEDDING_MODEL_ID,
    HF_CACHE,
)

def format_documents(documents):
    return "\n\n".join(document.page_content for document in documents)

# Page config
st.set_page_config(page_title="ChatRAG", page_icon="💬", layout="wide")

# Custom CSS
st.markdown("""
<style>
    /* Input field styling */
    .stTextInput > div > div > input {
        background-color: #f0f2f6 !important;
        color: #000000 !important;
    }
    
    /* Sidebar Background - Light Gray */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }
    
    /* Sidebar Content Area */
    [data-testid="stSidebarContent"] {
        background-color: #B0E0E6 !important;
    }
    
    /* Force all text inside sidebar to be black for readability on light bg */
    [data-testid="stSidebar"] * {
        color: #000000 !important;
    }
    
    /* Main chat area text */
    .stChatMessage {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    st.divider()
    
    # LLM Configuration
    st.subheader("🤖 LLM Settings")
    
    api_base = st.text_input(
        "API Base URL",
        value=st.session_state.get("api_base", DEFAULT_API_BASE),
        placeholder="http://localhost:1234/v1",
        help="LM Studio / vLLM / OpenAI-compatible API endpoint"
    )
    
    api_key = st.text_input(
        "API Key",
        value=st.session_state.get("api_key", DEFAULT_API_KEY),
        placeholder="sk-... or not-needed",
        type="password",
        help="API key (use 'not-needed' for local LM Studio)"
    )
    
    model_name = st.text_input(
        "Model Name",
        value=st.session_state.get("model_name", DEFAULT_MODEL_NAME),
        placeholder="llama-3.2-1b-instruct",
        help="Exact model name as shown in LM Studio / vLLM"
    )
    
    # Save to session state
    if st.button("💾 Save & Connect", type="primary", use_container_width=True):
        st.session_state.api_base = api_base
        st.session_state.api_key = api_key
        st.session_state.model_name = model_name
        
        # Test connection
        with st.spinner("Testing connection..."):
            try:
                llm = get_llm(api_base, api_key, model_name)
                verify_llm_model_availability(llm)
                st.session_state.llm = llm
                st.session_state.llm_connected = True
                st.success(f"✅ Connected! Model '{model_name}' is available.")
            except Exception as e:
                st.session_state.llm_connected = False
                st.error(f"❌ Connection failed: {e}")
    
    # Connection status
    if st.session_state.get("llm_connected"):
        st.success(f"🟢 Connected: `{st.session_state.get('model_name')}`")
    elif "api_base" in st.session_state:
        st.error("🔴 Not connected")
    
    st.divider()
    
    # Embedding Model Section - Supports Local Cache and Hugging Face API
    st.subheader("📦 Embedding Model")
    
    # Added Hugging Face API Key input field
    hf_api_key = st.text_input(
        "HuggingFace API Token",
        value=st.session_state.get("hf_api_key", ""),
        placeholder="hf_...",
        type="password",
        help="Required for downloading gated models or using HF Hub APIs."
    )
    
    # Show cache status
    cache_dir = Path(HF_CACHE) / "hub"
    model_dirs = list(cache_dir.glob(f"models--{EMBEDDING_MODEL_ID.replace('/', '--')}*")) if cache_dir.exists() else []
    if model_dirs:
        st.caption(f"📁 Found in cache: `{HF_CACHE}`")
    else:
        st.caption(f"📁 Cache: `{HF_CACHE}` (not found)")
    
    # Check if model is loaded
    if "embedding_model" in st.session_state and st.session_state.embedding_model is not None:
        st.success("✅ Embedding model loaded")
        if st.button("🔄 Reload Model", use_container_width=True):
            st.session_state.embedding_model = None
            st.rerun()
    else:
        st.warning("⚠️ Embedding model not loaded")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📂 Local Cache", use_container_width=True):
                with st.spinner("Loading from local cache..."):
                    try:
                        st.session_state.embedding_model = get_embedding_model(allow_download=False)
                        st.success("✅ Model loaded from local cache!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Cache load failed: {e}")
        
        with col2:
            if st.button("🌐 HuggingFace API", type="primary", use_container_width=True):
                with st.spinner(f"Loading {EMBEDDING_MODEL_ID} via HuggingFace..."):
                    try:
                        # Store API token in session state and set environment variable if provided
                        st.session_state.hf_api_key = hf_api_key
                        if hf_api_key.strip():
                            os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_api_key.strip()
                            os.environ["HF_TOKEN"] = hf_api_key.strip()

                        # Pass hf_token directly if supported by get_embedding_model or set via env vars above
                        st.session_state.embedding_model = get_embedding_model(
                            allow_download=True, 
                            token=hf_api_key.strip() if hf_api_key.strip() else None
                        )
                        st.success("✅ Model loaded via HuggingFace!")
                        st.rerun()
                    except TypeError:
                        # Fallback if get_embedding_model does not accept a 'token' parameter directly
                        st.session_state.embedding_model = get_embedding_model(allow_download=True)
                        st.success("✅ Model loaded via HuggingFace!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ HF API load failed: {e}")
    
    st.caption(f"Model: `{EMBEDDING_MODEL_ID}` (auto GPU/CPU)")
    
    st.divider()
    
    # Clear chat
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        if "qa_chain" in st.session_state:
            del st.session_state.qa_chain
        st.rerun()

# Main area
st.title("💬 ChatRAG")
st.caption("Chat with your documents using local LLMs")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# File uploader
uploaded_files = st.file_uploader(
    "📄 Upload documents (PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
    help="Upload one or more documents to chat with"
)

# Process uploaded files - only if embedding model is loaded
if uploaded_files and st.session_state.get("llm_connected"):
    if "embedding_model" not in st.session_state or st.session_state.embedding_model is None:
        st.warning("⚠️ Please load the embedding model first (sidebar)")
    elif "qa_chain" not in st.session_state or st.session_state.get("last_files") != [f.name for f in uploaded_files]:
        with st.spinner("Processing documents..."):
            # Load documents
            documents = []
            for uploaded_file in uploaded_files:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                try:
                    if uploaded_file.name.endswith(".pdf"):
                        loader = PyPDFLoader(tmp_path)
                    elif uploaded_file.name.endswith(".docx"):
                        loader = Docx2txtLoader(tmp_path)
                    else:
                        loader = TextLoader(tmp_path)
                    documents.extend(loader.load())
                finally:
                    os.unlink(tmp_path)
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_documents(documents)
            
            # Create vector store
            vectorstore = FAISS.from_documents(texts, st.session_state.embedding_model)
            
            # Create QA chain
            prompt_template = """Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Answer:"""
            PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
            
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            st.session_state.retriever = retriever
            st.session_state.qa_chain = (
                {"context": retriever | format_documents, "question": RunnablePassthrough()}
                | PROMPT
                | st.session_state.llm
                | StrOutputParser()
            )
            st.session_state.last_files = [f.name for f in uploaded_files]
            st.success(f"✅ Processed {len(uploaded_files)} document(s) into {len(texts)} chunks")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "sources" in message:
            with st.expander("📚 Sources"):
                for i, doc in enumerate(message["sources"]):
                    st.markdown(f"**Source {i+1}:** {doc.page_content[:200]}...")

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    if not st.session_state.get("llm_connected"):
        st.error("⚠️ Please configure and connect to an LLM first (sidebar)")
    elif "embedding_model" not in st.session_state or st.session_state.embedding_model is None:
        st.error("⚠️ Please load the embedding model first (sidebar)")
    elif "qa_chain" not in st.session_state:
        st.error("⚠️ Please upload at least one document first")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = st.session_state.qa_chain.invoke(prompt)
                    sources = st.session_state.retriever.invoke(prompt)
                    
                    st.markdown(answer)
                    
                    if sources:
                        with st.expander("📚 Sources"):
                            for i, doc in enumerate(sources):
                                st.markdown(f"**Source {i+1}:** {doc.page_content[:300]}...")
                    
                    # Add to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Error: {e}"
                    })

# Footer
st.divider()
st.caption("💡 Configure your LLM endpoint in the sidebar. Works with LM Studio, vLLM, Ollama (with OpenAI compat), or any OpenAI-compatible API.")