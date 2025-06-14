# main.py
import streamlit as st
from rag import create_rag_chain

def main():
    st.set_page_config(page_title="PDF Chat")
    st.header("Chat with your PDF 📄")
    
    # File upload
    pdf_docs = st.file_uploader(
        "Upload PDF(s)",
        type="pdf",
        accept_multiple_files=True
    )
    
    if pdf_docs and "rag_chain" not in st.session_state:
        with st.spinner("Processing..."):
            # Save uploaded files temporarily
            temp_paths = []
            for pdf in pdf_docs:
                with open(f"/tmp/{pdf.name}", "wb") as f:
                    f.write(pdf.getvalue())
                temp_paths.append(f"/tmp/{pdf.name}")
            
            # Create RAG chain
            st.session_state.rag_chain = create_rag_chain(temp_paths)
    
    # Chat interface
    if "rag_chain" in st.session_state:
        user_query = st.text_input("Ask a question about your PDF:")
        if user_query:
            with st.spinner("Thinking..."):
                response = st.session_state.rag_chain({"question": user_query})
                st.write("Answer:", response["answer"])

if __name__ == "__main__":
    main()