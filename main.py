# main.py
import streamlit as st
from rag import create_rag_chain, create_web_search_chain
import os
import tempfile
from langchain_core.messages import HumanMessage, AIMessage

# --- Page Configuration ---
st.set_page_config(
    page_title="Private GPT",
    page_icon="🤖",
    layout="wide"
)

# --- Session State Initialization ---
def initialize_session_state():
    """Initializes session state variables."""
    defaults = { "mode": "RAG", "messages": [], "uploaded_file_paths": [], "rag_chain": None, "web_search_chain": None }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# --- Helper Functions ---
def reset_rag_chain():
    """Resets the RAG chain and chat history."""
    st.session_state.rag_chain = None
    st.session_state.messages = []

def format_chat_history():
    """Formats chat history for the RAG chain."""
    history = []
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            history.append(HumanMessage(content=msg["content"]))
        else:
            answer_part = msg["content"].split("Sources:")[0].strip()
            history.append(AIMessage(content=answer_part))
    return history

def get_source_str(response):
    """Formats source documents from the 'context' key."""
    source_docs = response.get("context", [])
    if not source_docs: return ""
    
    sources_set = set()
    for doc in source_docs:
        source_name = os.path.basename(doc.metadata.get("source", "Unknown"))
        page_num = doc.metadata.get("page")
        source_info = f"{source_name}"
        if page_num is not None:
            source_info += f" (page {page_num + 1})"
        sources_set.add(source_info)
        
    return "Sources:\n" + "\n".join([f"- {s}" for s in sorted(list(sources_set))])


# --- UI Rendering ---
st.title("🤖 PRIVATE GPT")

# --- Sidebar ---
with st.sidebar:
    st.header("Controls")
    
    mode = st.radio("**Select Mode**", ("RAG", "Search"), key="mode", on_change=reset_rag_chain)
    st.markdown("---")

    if mode == "RAG":
        st.subheader("File Management")
        
        uploaded_files = st.file_uploader("Upload Your Documents", type=["pdf", "docx", "txt", "csv", "xlsx"], accept_multiple_files=True, label_visibility="collapsed")

        if uploaded_files:
            if 'temp_dir' not in st.session_state or not os.path.exists(st.session_state.temp_dir):
                st.session_state.temp_dir = tempfile.mkdtemp(prefix="gpt_files_")

            new_file_paths = []
            for file in uploaded_files:
                temp_path = os.path.join(st.session_state.temp_dir, file.name)
                with open(temp_path, "wb") as f:
                    f.write(file.getvalue())
                new_file_paths.append(temp_path)
            
            st.session_state.uploaded_file_paths = new_file_paths
            st.success(f"{len(new_file_paths)} file(s) loaded successfully!")
            reset_rag_chain()
        
        if st.session_state.uploaded_file_paths:
            st.markdown("**Ingested Files:**")
            for path in st.session_state.uploaded_file_paths:
                st.info(f"📄 {os.path.basename(path)}")
            
            if st.button("🗑️ Clear All Files"):
                st.session_state.uploaded_file_paths = []
                reset_rag_chain()
                st.rerun()

# --- Main Content Area ---
if st.session_state.mode == "RAG":
    st.info("Mode: **RAG** - Chat with your uploaded documents.")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask a question about your documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if not st.session_state.uploaded_file_paths:
                st.error("Please upload documents before asking questions.")
            else:
                if st.session_state.rag_chain is None:
                    with st.spinner("Processing documents and building RAG chain..."):
                        try:
                            st.session_state.rag_chain = create_rag_chain(st.session_state.uploaded_file_paths)
                        except Exception as e:
                            st.error(f"Failed to create RAG chain: {e}")
                
                if st.session_state.rag_chain:
                    with st.spinner("Thinking..."):
                        chat_history = format_chat_history()
                        response = st.session_state.rag_chain.invoke({"input": prompt, "chat_history": chat_history})
                        answer = response.get("answer", "Sorry, I couldn't find an answer.")
                        sources_str = get_source_str(response)
                        full_response = f"{answer}\n\n{sources_str}".strip()
                        st.markdown(full_response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})

elif st.session_state.mode == "Search":
    st.info("Mode: **Search** - Search the web for answers.")
    if st.session_state.web_search_chain is None:
        st.session_state.web_search_chain = create_web_search_chain()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Enter your web search query..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching the web and synthesizing answer..."):
                response = st.session_state.web_search_chain.invoke({"question": prompt})
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
