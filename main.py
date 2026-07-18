import streamlit as st
from models import get_embedding_model, get_llm, verify_llm_model_availability, DEFAULT_API_BASE, DEFAULT_API_KEY, DEFAULT_MODEL_NAME
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_core.prompts import PromptTemplate
import tempfile
import os

# Page config
st.set_page_config(page_title="ChatRAG", page_icon="💬", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stTextInput > div > div > input {
        background-color: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
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
    
    # Embedding Model - Load from Local Cache Only
    st.subheader("📦 Embedding Model")
    
    EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Show cache status
    import os
    hf_cache = os.getenv("HF_HOME", os.path.expanduser("~/.cache/huggingface"))
    from pathlib import Path
    cache_dir = Path(hf_cache) / "hub"
    model_dirs = list(cache_dir.glob(f"models--{EMBEDDING_MODEL_NAME.replace('/', '--')}--*")) if cache_dir.exists() else []
    if model_dirs:
        st.caption(f"📁 Found in cache: `{hf_cache}`")
    else:
        st.caption(f"📁 Cache: `{hf_cache}` (not found)")
    
    # Check if model is loaded
    if "embedding_model" in st.session_state and st.session_state.embedding_model is not None:
        st.success("✅ Embedding model loaded")
        if st.button("🔄 Reload Model", use_container_width=True):
            st.session_state.embedding_model = None
            st.rerun()
    else:
        st.warning("⚠️ Embedding model not loaded")
        if st.button("📂 Load from Cache", type="primary", use_container_width=True):
            with st.spinner(f"Loading {EMBEDDING_MODEL_NAME} from local cache..."):
                try:
                    st.session_state.embedding_model = get_embedding_model()
                    st.success("✅ Embedding model loaded successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to load model: {type(e).__name__}: {e}")
                    with st.expander("🔍 Fix: Pre-download the model first"):
                        st.markdown(f"""
                        **The model must be pre-downloaded to the local cache.**
                        
                        Run this once (with internet):
                        ```bash
                        python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('{EMBEDDING_MODEL_NAME}')"
                        ```
                        
                        Or set custom cache:
                        ```bash
                        export HF_HOME=/path/to/cache
                        python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('{EMBEDDING_MODEL_NAME}')"
                        ```
                        
                        Then restart the app.
                        """)
    
    st.caption(f"Model: `{EMBEDDING_MODEL_NAME}` (auto GPU/CPU)")
    
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
        st.warning("⚠️ Please download the embedding model first (sidebar)")
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
            
            st.session_state.qa_chain = RetrievalQA.from_chain_type(
                llm=st.session_state.llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                chain_type_kwargs={"prompt": PROMPT},
                return_source_documents=True
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
        st.error("⚠️ Please download the embedding model first (sidebar)")
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
                    result = st.session_state.qa_chain({"query": prompt})
                    answer = result["result"]
                    sources = result.get("source_documents", [])
                    
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