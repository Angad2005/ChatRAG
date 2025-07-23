# # main.py
# import streamlit as st
# from rag import create_rag_chain
# import os

# def main():
#     st.set_page_config(page_title="Document Chat")
#     st.header("Chat with your Documents 📁")
    
#     # File upload (supporting multiple formats)
#     uploaded_files = st.file_uploader(
#         "Upload Documents",
#         type=["pdf", "docx", "txt", "csv", "xlsx"],
#         accept_multiple_files=True
#     )
    
#     if uploaded_files and "rag_chain" not in st.session_state:
#         with st.spinner("Processing documents..."):
#             # Save files temporarily
#             temp_paths = []
#             for file in uploaded_files:
#                 temp_path = f"/tmp/{file.name}"
#                 with open(temp_path, "wb") as f:
#                     f.write(file.getvalue())
#                 temp_paths.append(temp_path)
            
#             # Create RAG chain
#             try:
#                 st.session_state.rag_chain = create_rag_chain(temp_paths)
#             except Exception as e:
#                 st.error(f"Error processing files: {str(e)}")
#                 # Clean up temp files on error
#                 for path in temp_paths:
#                     os.remove(path)
    
#     # Chat interface
#     if "rag_chain" in st.session_state:
#         user_query = st.text_input("Ask a question about your documents:")
#         if user_query:
#             with st.spinner("Thinking..."):
#                 response = st.session_state.rag_chain({"question": user_query})
#                 st.write("Answer:", response["answer"])

# if __name__ == "__main__":
#     main()


import streamlit as st
import os
import shutil
from rag import create_rag_chain, summarize_documents

# --- Page and Session Initialization ---
# This MUST be the first Streamlit command.
st.set_page_config(page_title="Document Chat")

# This part runs only once per new session/browser tab
if "app_started" not in st.session_state:
    st.session_state.app_started = True
    st.session_state.rag_chain = None
    st.session_state.summaries = {}
    st.session_state.uploaded_files_cache = []
    st.session_state.show_summary = False

    # Clean the vector store at the very beginning of a new session
    if os.path.exists("vectorstore"):
        with st.spinner("Cleaning up old vector store..."):
            shutil.rmtree("vectorstore")
        st.toast("A new session has started. Old documents cleared.")

def main():
    st.header("Chat with your Documents 📁")

    # Sidebar for actions
    with st.sidebar:
        st.subheader("Manage Documents")

        uploaded_files = st.file_uploader(
            "Upload documents to add to the knowledge base",
            type=["pdf", "docx", "txt", "csv", "xlsx"],
            accept_multiple_files=True
        )

        if st.button("Summarize Documents"):
            if st.session_state.rag_chain:
                st.session_state.show_summary = True
            else:
                st.warning("Please upload and process documents first.")

        if st.button("Delete All Documents & Reset"):
            with st.spinner("Deleting documents and resetting session..."):
                if os.path.exists("vectorstore"):
                    shutil.rmtree("vectorstore")
                # Reset the session state completely
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("All documents and chat history have been deleted.")
                st.rerun()

    # --- Main Processing Logic ---
    # Check if the list of uploaded files has changed to avoid reprocessing
    if uploaded_files and uploaded_files != st.session_state.uploaded_files_cache:
        st.session_state.uploaded_files_cache = uploaded_files

        with st.spinner("Processing documents... This may take a moment."):
            temp_dir = "/tmp/rag_files"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            temp_paths = []
            for file in uploaded_files:
                temp_path = os.path.join(temp_dir, file.name)
                with open(temp_path, "wb") as f:
                    f.write(file.getvalue())
                temp_paths.append(temp_path)
            
            try:
                # Create RAG chain with ALL currently uploaded files in the session
                rag_chain, docs = create_rag_chain(temp_paths)
                st.session_state.rag_chain = rag_chain
                st.session_state.summaries = summarize_documents(docs)
                st.success(f"{len(uploaded_files)} document(s) processed successfully!")
            
            except Exception as e:
                st.error(f"Error processing files: {str(e)}")
            
            finally:
                # Clean up the temporary directory
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

    # --- UI Display ---
    if st.session_state.get("show_summary"):
        st.subheader("Summary of Currently Loaded Documents")
        if st.session_state.summaries:
            for filename, summary in st.session_state.summaries.items():
                with st.expander(f"**{os.path.basename(filename)}**"):
                    st.write(summary)
        else:
            st.info("No summaries available.")
        # Reset the flag so the summary doesn't show up again on its own
        st.session_state.show_summary = False

    if st.session_state.rag_chain:
        st.info("Your documents are ready. Ask a question below.")
        user_query = st.text_input("Ask a question about your documents:")
        if user_query:
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.rag_chain({"question": user_query})
                    st.write("### Answer")
                    st.write(response["answer"])
                except Exception as e:
                    st.error(f"An error occurred: {e}")
    else:
        st.info("Upload documents via the sidebar to begin chatting.")

if __name__ == "__main__":
    main()