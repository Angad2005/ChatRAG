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

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="ChatRAG • Private Document AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom Modern UI Styling (CSS)
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Hero Header Styling */
    .hero-container {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(168, 85, 247, 0.08) 100%);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
    }
    
    .hero-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 6px;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        color: #64748B;
        font-size: 0.95rem;
        margin: 0;
    }

    /* Status Pill / Chip */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .status-connected {
        background-color: #ECFDF5;
        color: #059669;
        border: 1px solid #A7F3D0;
    }
    
    .status-disconnected {
        background-color: #FEF2F2;
        color: #DC2626;
        border: 1px solid #FECACA;
    }

    /* Metric & Feature Cards */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }
    
    .metric-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        font-weight: 600;
    }
    
    .metric-value {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1E293B;
        margin-top: 4px;
    }

    /* Source Cards in Chat */
    .source-box {
        background: #F8FAFC;
        border-left: 3px solid #6366F1;
        border-radius: 4px 8px 8px 4px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 0.85rem;
        color: #334155;
    }

    /* Input & Button Refinements */
    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 1px solid #E2E8F0 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }

    /* Primary Buttons */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.35) !important;
    }

    /* Chat Messages */
    .stChatMessage {
        border-radius: 12px !important;
        padding: 14px 16px !important;
        margin-bottom: 12px !important;
        border: 1px solid #F1F5F9 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def format_documents(documents):
    return "\n\n".join(document.page_content for document in documents)

# ---------------------------------------------------------
# Sidebar Configuration
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Workspace Control")
    st.caption("Manage LLM inference endpoints & vector embeddings")
    
    tab_llm, tab_embed, tab_status = st.tabs(["🤖 Model", "📦 Embeddings", "📊 Status"])
    
    with tab_llm:
        st.markdown("##### **Inference Endpoint**")
        api_base = st.text_input(
            "API Base URL",
            value=st.session_state.get("api_base", DEFAULT_API_BASE),
            placeholder="http://localhost:1234/v1",
            help="LM Studio, vLLM, Ollama, or OpenAI API URL"
        )
        
        api_key = st.text_input(
            "API Key",
            value=st.session_state.get("api_key", DEFAULT_API_KEY),
            placeholder="sk-... or 'not-needed'",
            type="password",
            help="API Key for the provider"
        )
        
        model_name = st.text_input(
            "Model Identifier",
            value=st.session_state.get("model_name", DEFAULT_MODEL_NAME),
            placeholder="llama-3.2-1b-instruct",
            help="Exact identifier registered on your local/remote server"
        )
        
        if st.button("⚡ Connect LLM", type="primary", use_container_width=True):
            st.session_state.api_base = api_base
            st.session_state.api_key = api_key
            st.session_state.model_name = model_name
            
            with st.spinner("Establishing connection..."):
                try:
                    llm = get_llm(api_base, api_key, model_name)
                    verify_llm_model_availability(llm)
                    st.session_state.llm = llm
                    st.session_state.llm_connected = True
                    st.toast(f"Connected to {model_name}!", icon="🟢")
                    st.rerun()
                except Exception as e:
                    st.session_state.llm_connected = False
                    st.error(f"Connection failed: {e}")

    with tab_embed:
        st.markdown("##### **Vector Embedding Engine**")
        hf_api_key = st.text_input(
            "HuggingFace Token (Optional)",
            value=st.session_state.get("hf_api_key", ""),
            placeholder="hf_...",
            type="password",
            help="Needed for gated models or downloading from HF Hub"
        )
        
        cache_dir = Path(HF_CACHE) / "hub"
        model_dirs = list(cache_dir.glob(f"models--{EMBEDDING_MODEL_ID.replace('/', '--')}*")) if cache_dir.exists() else []
        
        if model_dirs:
            st.success(f"💾 Found in Local Cache", icon="✅")
        else:
            st.info(f"🌐 Not in local cache (will download)", icon="ℹ️")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📂 Local Cache", use_container_width=True):
                with st.spinner("Loading cached weights..."):
                    try:
                        st.session_state.embedding_model = get_embedding_model(allow_download=False)
                        st.toast("Loaded from cache!", icon="✅")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Cache load error: {e}")

        with col2:
            if st.button("🌐 Fetch Hub", type="primary", use_container_width=True):
                with st.spinner("Fetching model..."):
                    try:
                        st.session_state.hf_api_key = hf_api_key
                        if hf_api_key.strip():
                            os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_api_key.strip()
                            os.environ["HF_TOKEN"] = hf_api_key.strip()

                        st.session_state.embedding_model = get_embedding_model(
                            allow_download=True,
                            token=hf_api_key.strip() if hf_api_key.strip() else None
                        )
                        st.toast("Model downloaded & loaded!", icon="🚀")
                        st.rerun()
                    except TypeError:
                        st.session_state.embedding_model = get_embedding_model(allow_download=True)
                        st.rerun()
                    except Exception as e:
                        st.error(f"HF Hub fetch error: {e}")

        st.caption(f"Model ID: `{EMBEDDING_MODEL_ID}`")

    with tab_status:
        st.markdown("##### **System Diagnostics**")
        
        # LLM Status Pill
        if st.session_state.get("llm_connected"):
            st.markdown(f'<span class="status-badge status-connected">● LLM Active ({st.session_state.get("model_name")})</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge status-disconnected">● LLM Offline</span>', unsafe_allow_html=True)
        
        st.write("")
        # Embedding Status Pill
        if "embedding_model" in st.session_state and st.session_state.embedding_model is not None:
            st.markdown('<span class="status-badge status-connected">● Embeddings Loaded</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge status-disconnected">● Embeddings Not Ready</span>', unsafe_allow_html=True)
        
        st.divider()
        if st.button("🗑️ Reset Session & Chat", use_container_width=True):
            st.session_state.messages = []
            if "qa_chain" in st.session_state:
                del st.session_state.qa_chain
            st.rerun()

# ---------------------------------------------------------
# Main Page Header & Metrics
# ---------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-title">💬 ChatRAG Studio</div>
    <p class="hero-subtitle">High-performance Retrieval-Augmented Generation powered by LangChain & FAISS.</p>
</div>
""", unsafe_allow_html=True)

# Metric Summary Bar
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    llm_name = st.session_state.get("model_name", "None") if st.session_state.get("llm_connected") else "Disconnected"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Active LLM</div>
        <div class="metric-value">{llm_name}</div>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    embed_status = "Ready" if ("embedding_model" in st.session_state and st.session_state.embedding_model is not None) else "Not Loaded"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Embedding Vectorizer</div>
        <div class="metric-value">{embed_status}</div>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    doc_count = len(st.session_state.get("last_files", []))
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Indexed Documents</div>
        <div class="metric-value">{doc_count} File(s)</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------
# Document Ingestion Area
# ---------------------------------------------------------
with st.expander("📂 **Document Ingestion & Knowledge Base**", expanded=not bool(st.session_state.get("last_files"))):
    uploaded_files = st.file_uploader(
        "Upload files for context chunking",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help="Supports PDF, DOCX, and Plain Text files"
    )

    if uploaded_files and st.session_state.get("llm_connected"):
        if "embedding_model" not in st.session_state or st.session_state.embedding_model is None:
            st.warning("⚠️ Please load an Embedding Model from the sidebar first.")
        elif "qa_chain" not in st.session_state or st.session_state.get("last_files") != [f.name for f in uploaded_files]:
            with st.status("🔄 Building FAISS Vector Index...", expanded=True) as status:
                st.write("Extracting text streams...")
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

                st.write(f"Generating recursive chunks (size: 1000, overlap: 200)...")
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                texts = text_splitter.split_documents(documents)

                st.write(f"Embedding {len(texts)} chunks into FAISS vector space...")
                vectorstore = FAISS.from_documents(texts, st.session_state.embedding_model)

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
                status.update(label=f"✅ Successfully indexed {len(uploaded_files)} file(s) into {len(texts)} chunks!", state="complete", expanded=False)

# ---------------------------------------------------------
# Chat Interface
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "⚡"):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "sources" in message and message["sources"]:
            with st.expander("📚 Retrieved Knowledge Snippets"):
                for i, doc in enumerate(message["sources"]):
                    st.markdown(f"""
                    <div class="source-box">
                        <strong>Source Chunk {i+1}</strong><br>
                        {doc.page_content[:350]}...
                    </div>
                    """, unsafe_allow_html=True)

# Empty state prompt helper
if not st.session_state.messages:
    st.info("💡 **Ready to chat!** Upload your documents above and make sure your LLM & Embeddings are connected in the sidebar.", icon="✨")

# User Input
if prompt := st.chat_input("Ask anything about your uploaded documents..."):
    if not st.session_state.get("llm_connected"):
        st.error("⚠️ Please configure and connect your LLM in the sidebar first.")
    elif "embedding_model" not in st.session_state or st.session_state.embedding_model is None:
        st.error("⚠️ Please load the embedding model in the sidebar.")
    elif "qa_chain" not in st.session_state:
        st.error("⚠️ Please upload and index at least one document first.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚡"):
            with st.spinner("Synthesizing answer from document chunks..."):
                try:
                    answer = st.session_state.qa_chain.invoke(prompt)
                    sources = st.session_state.retriever.invoke(prompt)
                    
                    st.markdown(answer)
                    
                    if sources:
                        with st.expander("📚 Retrieved Knowledge Snippets"):
                            for i, doc in enumerate(sources):
                                st.markdown(f"""
                                <div class="source-box">
                                    <strong>Source Chunk {i+1}</strong><br>
                                    {doc.page_content[:350]}...
                                </div>
                                """, unsafe_allow_html=True)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                except Exception as e:
                    st.error(f"Generation error: {e}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"⚠️ Error: {e}"
                    })
