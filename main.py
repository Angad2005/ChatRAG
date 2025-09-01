# # main.py
# import streamlit as st
# import os
# import shutil
# from rag import create_rag_chain, summarize_documents

# # --- Page and Session Initialization ---
# st.set_page_config(page_title="Document Chat")

# # This part runs only once per new session/browser tab
# if "app_started" not in st.session_state:
#     st.session_state.app_started = True
#     st.session_state.rag_chain = None
#     st.session_state.summaries = {}
#     st.session_state.uploaded_files_cache = []
#     st.session_state.show_summary = False
#     st.session_state.uploader_key = 0  # Initialize the key for the file uploader

#     # Clean the vector store at the very beginning of a new session
#     if os.path.exists("vectorstore"):
#         shutil.rmtree("vectorstore")
#         st.toast("A new session has started. Old documents cleared.")

# def reset_session():
#     """Callback function to reset the session and clear the file uploader."""
#     st.session_state.rag_chain = None
#     st.session_state.summaries = {}
#     st.session_state.uploaded_files_cache = []
#     st.session_state.show_summary = False
    
#     # Increment the key to force the file_uploader to re-render as a new widget
#     st.session_state.uploader_key += 1
    
#     if os.path.exists("vectorstore"):
#         shutil.rmtree("vectorstore")
    
#     st.success("All documents and chat history have been deleted.")

# def main():
#     st.header("Chat with your Documents 📁")

#     # Sidebar for actions
#     with st.sidebar:
#         st.subheader("Manage Documents")

#         # --> MODIFIED CODE: Use the session state key for the file uploader <--
#         uploaded_files = st.file_uploader(
#             "Upload documents to add to the knowledge base",
#             type=["pdf", "docx", "txt", "csv", "xlsx"],
#             accept_multiple_files=True,
#             key=f"uploader_{st.session_state.uploader_key}"
#         )

#         if st.button("Summarize Documents"):
#             if st.session_state.get("rag_chain"):
#                 st.session_state.show_summary = True
#             else:
#                 st.warning("Please upload and process documents first.")
        
#         # --> MODIFIED CODE: The on_click now points to the improved reset function <--
#         st.button("Delete All Documents & Reset", on_click=reset_session)

#     # --- Main Processing Logic ---
#     if uploaded_files and uploaded_files != st.session_state.get("uploaded_files_cache"):
#         st.session_state.uploaded_files_cache = uploaded_files

#         with st.spinner("Processing documents... This may take a moment. If Response not there in 1 minute then issue with API or endpoint configuration."):
#             temp_dir = "/tmp/rag_files"
#             if not os.path.exists(temp_dir):
#                 os.makedirs(temp_dir)
            
#             temp_paths = []
#             for file in uploaded_files:
#                 temp_path = os.path.join(temp_dir, file.name)
#                 with open(temp_path, "wb") as f:
#                     f.write(file.getvalue())
#                 temp_paths.append(temp_path)
            
#             try:
#                 rag_chain, docs = create_rag_chain(temp_paths)
#                 st.session_state.rag_chain = rag_chain
#                 st.session_state.summaries = summarize_documents(docs)
#                 st.success(f"{len(uploaded_files)} document(s) processed successfully!")
            
#             except Exception as e:
#                 st.error(f"Error processing files: {str(e)}")
            
#             finally:
#                 if os.path.exists(temp_dir):
#                     shutil.rmtree(temp_dir)

#     # --- UI Display ---
#     if st.session_state.get("show_summary"):
#         st.subheader("Summary of Currently Loaded Documents")
#         if st.session_state.get("summaries"):
#             for filename, summary in st.session_state.summaries.items():
#                 with st.expander(f"**{os.path.basename(filename)}**"):
#                     st.write(summary)
#         else:
#             st.info("No summaries available.")
#         st.session_state.show_summary = False

#     if st.session_state.get("rag_chain"):
#         st.info("Your documents are ready. Ask a question below.")
#         user_query = st.text_input("Ask a question about your documents:")
#         if user_query:
#             with st.spinner("Thinking..."):
#                 try:
#                     response = st.session_state.rag_chain({"question": user_query})
#                     st.write("### Answer")
#                     st.write(response["answer"])
#                 except Exception as e:
#                     st.error(f"An error occurred: {e}")
#     else:
#         st.info("Upload documents via the sidebar to begin chatting. Testing and API configuration is user dependent.")

# if __name__ == "__main__":
#     main()

# main.py
import streamlit as st
import os
import shutil
from rag import create_rag_chain, summarize_documents
from models import verify_llm_model_availability

st.set_page_config(page_title="Document Chat")

if "app_started" not in st.session_state:
    st.session_state.app_started = True
    st.session_state.rag_chain = None
    st.session_state.summaries = {}
    st.session_state.uploaded_files_cache = []
    st.session_state.show_summary = False
    st.session_state.uploader_key = 0
    st.session_state.docs = [] # Keep track of loaded docs for summarization

    if os.path.exists("vectorstore"):
        shutil.rmtree("vectorstore")
        st.toast("A new session has started. Old documents cleared.")

def reset_session():
    st.session_state.rag_chain = None
    st.session_state.summaries = {}
    st.session_state.uploaded_files_cache = []
    st.session_state.show_summary = False
    st.session_state.uploader_key += 1
    st.session_state.docs = []
    if os.path.exists("vectorstore"):
        shutil.rmtree("vectorstore")
    st.success("All documents and chat history have been deleted.")

def main():
    st.header("Chat with your Documents 📁")

    with st.sidebar:
        st.subheader("Manage Documents")
        uploaded_files = st.file_uploader(
            "Upload documents",
            type=["pdf", "docx", "txt", "csv", "xlsx"],
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.uploader_key}"
        )

        # --> START OF MODIFIED CODE <--
        # This button now triggers the summarization call to the MCP
        if st.button("Summarize Documents"):
            if st.session_state.get("docs"):
                with st.spinner("Generating summaries via MCP..."):
                    try:
                        # Call the new MCP-based summarization function
                        st.session_state.summaries = summarize_documents(st.session_state.docs)
                        st.session_state.show_summary = True
                    except Exception as e:
                        st.error(f"Failed to get summaries: {e}")
            else:
                st.warning("Please upload and process documents first.")
        # --> END OF MODIFIED CODE <--
        
        st.button("Delete All Documents & Reset", on_click=reset_session)

    if uploaded_files and uploaded_files != st.session_state.get("uploaded_files_cache"):
        st.session_state.uploaded_files_cache = uploaded_files
        with st.spinner("Processing documents..."):
            temp_dir = "/tmp/rag_files"
            os.makedirs(temp_dir, exist_ok=True)
            
            temp_paths = [os.path.join(temp_dir, f.name) for f in uploaded_files]
            for file, path in zip(uploaded_files, temp_paths):
                with open(path, "wb") as f:
                    f.write(file.getvalue())
            
            try:
                rag_chain, docs = create_rag_chain(temp_paths)
                with st.spinner("Verifying language model connection..."):
                    llm_client = rag_chain.combine_docs_chain.llm_chain.llm
                    verify_llm_model_availability(llm_client)
                
                st.session_state.rag_chain = rag_chain
                st.session_state.docs = docs  # Save the docs for on-demand summarization
                # --> REMOVED: No longer summarizing on initial processing <--
                # st.session_state.summaries = summarize_documents(docs) 
                st.success(f"{len(uploaded_files)} document(s) processed successfully!")
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            
            finally:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

    # --- UI Display (No changes below this line) ---
    if st.session_state.get("show_summary"):
        st.subheader("Summary of Currently Loaded Documents")
        if st.session_state.get("summaries"):
            for filename, summary in st.session_state.summaries.items():
                with st.expander(f"**{os.path.basename(filename)}**"):
                    st.write(summary)
        else:
            st.info("No summaries available or an error occurred.")
        st.session_state.show_summary = False

    if st.session_state.get("rag_chain"):
        st.info("Your documents are ready. Ask a question below.")
        user_query = st.text_input("Ask a question about your documents:")
        if user_query:
            with st.spinner("Thinking..."):
                try:
                    retriever = st.session_state.rag_chain.retriever
                    relevant_docs = retriever.get_relevant_documents(user_query)
                    if not relevant_docs:
                        st.write("### Answer")
                        st.warning("I could not find an answer in the documents. Please try rephrasing.")
                    else:
                        response = st.session_state.rag_chain({"question": user_query})
                        st.write("### Answer")
                        st.write(response["answer"])
                except Exception as e:
                    st.error(f"An error occurred during generation: {e}")
    else:
        st.info("Upload documents via the sidebar to begin chatting.")

if __name__ == "__main__":
    main()