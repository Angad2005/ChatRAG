import gradio as gr
import os
from pathlib import Path

# Import your existing logic modules
from models import get_embedding_model, get_llm, verify_llm_model_availability, DEFAULT_API_BASE, DEFAULT_API_KEY, DEFAULT_MODEL_NAME
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# --- Helper Functions ---

def format_documents(documents):
    return "\n\n".join(document.page_content for document in documents)

def check_embedding_cache():
    """Check if embedding model exists in local cache"""
    EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    hf_cache = os.getenv("HF_HOME", os.path.expanduser("~/.cache/huggingface"))
    cache_dir = Path(hf_cache) / "hub"
    if cache_dir.exists():
        model_dirs = list(cache_dir.glob(f"models--{EMBEDDING_MODEL_NAME.replace('/', '--')}*"))
    else:
        model_dirs = []
    return len(model_dirs) > 0, hf_cache

def load_embedding_model_fn():
    """Load embedding model into session state"""
    try:
        model = get_embedding_model()
        return model, "✅ Embedding model loaded successfully!", gr.update(interactive=True)
    except Exception as e:
        return None, f"❌ Failed: {type(e).__name__}: {e}", gr.update(interactive=False)

def connect_llm_fn(api_base, api_key, model_name):
    """Test and save LLM connection"""
    try:
        llm = get_llm(api_base, api_key, model_name)
        verify_llm_model_availability(llm)
        return llm, True, f"🟢 Connected: `{model_name}`", gr.update(value=f"Connected to {model_name}")
    except Exception as e:
        return None, False, f"🔴 Connection failed: {e}", gr.update(value="Not connected")

def process_single_file(uploaded_file):
    """Helper to process a single uploaded file object from Gradio"""
    docs = []
    if uploaded_file is None:
        return docs
        
    # Handle Gradio file object (modern Gradio passes a dict)
    if isinstance(uploaded_file, dict):
        original_name = uploaded_file.get("orig_name", uploaded_file.get("name", "unknown.txt"))
        file_path = uploaded_file.get("name")
    else:
        original_name = getattr(uploaded_file, 'orig_name', getattr(uploaded_file, 'name', 'unknown.txt'))
        file_path = getattr(uploaded_file, 'name', str(uploaded_file))
        
    if not file_path or not os.path.exists(file_path):
        return docs

    suffix = os.path.splitext(original_name)[1]
    
    try:
        if suffix.lower().endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif suffix.lower().endswith(".docx"):
            loader = Docx2txtLoader(file_path)
        else:
            loader = TextLoader(file_path)
        docs.extend(loader.load())
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        
    return docs

def process_documents_fn(uploaded_files, llm, embedding_model):
    """Process uploaded files and create QA chain"""
    if not uploaded_files:
        return None, None, "⚠️ Please upload at least one document."
    if llm is None:
        return None, None, "⚠️ Please connect to an LLM first."
    if embedding_model is None:
        return None, None, "⚠️ Please load the embedding model first."

    documents = []
    if isinstance(uploaded_files, list):
        for f in uploaded_files:
            documents.extend(process_single_file(f))
    else:
        documents.extend(process_single_file(uploaded_files))
            
    if not documents:
        return None, None, "⚠️ No valid content found in uploaded files."

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    vectorstore = FAISS.from_documents(texts, embedding_model)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    prompt_template = """Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Answer:"""
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    
    qa_chain = (
        {"context": retriever | format_documents, "question": RunnablePassthrough()}
        | PROMPT
        | llm
        | StrOutputParser()
    )
    
    return qa_chain, retriever, f"✅ Processed {len(documents)} doc(s) into {len(texts)} chunks"

def chat_fn(message, history, qa_chain, retriever):
    """Handle chat message with sources"""
    if history is None:
        history = []
        
    if not message:
        return history
        
    if qa_chain is None or retriever is None:
        return history + [
            {"role": "user", "content": message}, 
            {"role": "assistant", "content": "⚠️ Please upload documents and ensure LLM/embeddings are loaded."}
        ]
    
    try:
        answer = qa_chain.invoke(message)
        sources = retriever.invoke(message)
        
        response_with_sources = str(answer)
        if sources:
            source_text = "\n\n**Sources:**\n"
            for i, doc in enumerate(sources):
                content_preview = doc.page_content[:300].replace('\n', ' ')
                source_text += f"- **Source {i+1}:** {content_preview}...\n"
            response_with_sources += source_text
            
        return history + [
            {"role": "user", "content": message}, 
            {"role": "assistant", "content": response_with_sources}
        ]
    except Exception as e:
        return history + [
            {"role": "user", "content": message}, 
            {"role": "assistant", "content": f"❌ Error: {str(e)}"}
        ]

def clear_chat_fn():
    """Clear chat history"""
    return [], None, None

# --- Gradio UI ---

theme = gr.themes.Default(
    primary_hue="blue",
    secondary_hue="cyan",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui"],
).set(
    body_background_fill="#1e3a8a",
    block_background_fill="#f8f9fa",
    block_border_width="1px",
    block_shadow="*shadow_drop_lg",
)

with gr.Blocks(title="ChatRAG") as demo:
    gr.Markdown("# 💬 ChatRAG\nChat with your documents using local LLMs")
    
    llm_state = gr.State(None)
    llm_connected_state = gr.State(False)
    embedding_state = gr.State(None)
    qa_chain_state = gr.State(None)
    retriever_state = gr.State(None)
    
    with gr.Row():
        with gr.Column(scale=1, elem_id="sidebar-panel"):
            gr.Markdown("## ⚙️ Configuration")
            
            gr.Markdown("### 🤖 LLM Settings")
            api_base_input = gr.Textbox(
                label="API Base URL", 
                value=DEFAULT_API_BASE,
                placeholder="http://localhost:1234/v1",
                info="LM Studio / vLLM / OpenAI-compatible endpoint"
            )
            api_key_input = gr.Textbox(
                label="API Key", 
                value=DEFAULT_API_KEY,
                placeholder="sk-... or not-needed",
                type="password",
                info="Use 'not-needed' for local LM Studio"
            )
            model_name_input = gr.Textbox(
                label="Model Name", 
                value=DEFAULT_MODEL_NAME,
                placeholder="llama-3.2-1b-instruct",
                info="Exact model name from your server"
            )
            
            connect_btn = gr.Button("💾 Save & Connect", variant="primary", size="lg")
            connection_status = gr.Textbox(label="Status", value="Not connected", interactive=False)
            
            gr.Markdown("---")
            
            gr.Markdown("### 📦 Embedding Model")
            cache_found, cache_path = check_embedding_cache()
            cache_info = gr.Markdown(f"📁 Cache: `{cache_path}` {'✅ Found' if cache_found else '❌ Not found'}")
            embedding_status = gr.Textbox(label="Embedding Status", value="⚠️ Not loaded", interactive=False)
            
            load_emb_btn = gr.Button("📂 Load from Cache", variant="primary", size="lg", interactive=cache_found)
            reload_emb_btn = gr.Button("🔄 Reload Model", size="sm", visible=False)
            
            gr.Markdown("---")
            
            gr.Markdown("### 📄 Documents")
            file_upload = gr.File(
                label="Upload PDF, DOCX, TXT",
                file_types=[".pdf", ".docx", ".txt"],
                file_count="multiple"
            )
            process_btn = gr.Button("🔧 Process Documents", variant="secondary")
            process_status = gr.Textbox(label="Processing Status", interactive=False)
            
            gr.Markdown("---")
            clear_btn = gr.Button("🗑️ Clear Chat", variant="stop")
        
        with gr.Column(scale=2):
            # FIXED: Removed type="messages" as it is the mandatory default in Gradio 6+ and causes a TypeError if explicitly passed
            chatbot = gr.Chatbot(
                label="Chat",
                height=500
            )
            msg_input = gr.Textbox(
                label="Ask a question...",
                placeholder="Type your question about the documents...",
                lines=2
            )
            send_btn = gr.Button("Send", variant="primary")
    
    # --- Event Handlers ---
    connect_btn.click(
        fn=connect_llm_fn,
        inputs=[api_base_input, api_key_input, model_name_input],
        outputs=[llm_state, llm_connected_state, connection_status, connection_status]
    )
    
    load_emb_btn.click(
        fn=load_embedding_model_fn,
        inputs=[],
        outputs=[embedding_state, embedding_status, reload_emb_btn]
    ).then(lambda: gr.update(visible=True), outputs=[reload_emb_btn])
    
    reload_emb_btn.click(
        fn=lambda: (None, "⚠️ Reloading...", gr.update(visible=False)),
        outputs=[embedding_state, embedding_status, reload_emb_btn]
    ).then(
        fn=load_embedding_model_fn,
        outputs=[embedding_state, embedding_status, reload_emb_btn]
    )
    
    process_btn.click(
        fn=process_documents_fn,
        inputs=[file_upload, llm_state, embedding_state],
        outputs=[qa_chain_state, retriever_state, process_status]
    )
    
    send_btn.click(
        fn=chat_fn,
        inputs=[msg_input, chatbot, qa_chain_state, retriever_state],
        outputs=[chatbot]
    ).then(lambda: "", outputs=[msg_input])
    
    msg_input.submit(
        fn=chat_fn,
        inputs=[msg_input, chatbot, qa_chain_state, retriever_state],
        outputs=[chatbot]
    ).then(lambda: "", outputs=[msg_input])
    
    clear_btn.click(
        fn=clear_chat_fn,
        outputs=[chatbot, qa_chain_state, retriever_state]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0", 
        server_port=7860,
        theme=theme,
        css="""
            .gradio-container { max-width: 1200px !important; }
            
            /* Dark theme for the configuration sidebar */
            #sidebar-panel { 
                background-color: #1e293b !important; 
                color: #f1f5f9 !important; 
                border-radius: 12px; 
                padding: 1rem; 
            }
            
            /* Ensure inner elements match the dark sidebar theme */
            #sidebar-panel .gr-box, 
            #sidebar-panel .gr-input, 
            #sidebar-panel .gr-button,
            #sidebar-panel .gr-dropdown { 
                background-color: #334155 !important; 
                color: #f1f5f9 !important; 
                border-color: #475569 !important; 
            }
            
            .chatbot { height: 500px !important; }
        """
    )