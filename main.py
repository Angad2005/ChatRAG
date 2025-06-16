# main.py
import streamlit as st
from rag import create_rag_chain
import os

def main():
    st.set_page_config(page_title="Document Chat")
    st.header("Chat with your Documents 📁")
    
    # File upload (supporting multiple formats)
    uploaded_files = st.file_uploader(
        "Upload Documents",
        type=["pdf", "docx", "txt", "csv", "xlsx"],
        accept_multiple_files=True
    )
    
    if uploaded_files and "rag_chain" not in st.session_state:
        with st.spinner("Processing documents..."):
            # Save files temporarily
            temp_paths = []
            for file in uploaded_files:
                temp_path = f"/tmp/{file.name}"
                with open(temp_path, "wb") as f:
                    f.write(file.getvalue())
                temp_paths.append(temp_path)
            
            # Create RAG chain
            try:
                st.session_state.rag_chain = create_rag_chain(temp_paths)
            except Exception as e:
                st.error(f"Error processing files: {str(e)}")
                # Clean up temp files on error
                for path in temp_paths:
                    os.remove(path)
    
    # Chat interface
    if "rag_chain" in st.session_state:
        user_query = st.text_input("Ask a question about your documents:")
        if user_query:
            with st.spinner("Thinking..."):
                response = st.session_state.rag_chain({"question": user_query})
                st.write("Answer:", response["answer"])

if __name__ == "__main__":
    main()