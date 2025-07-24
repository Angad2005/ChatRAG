# # rag.py
# from langchain.vectorstores import FAISS
# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferMemory
# from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, CSVLoader, UnstructuredExcelLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from models import get_llm, get_embedding_model

# def create_rag_chain(file_paths):
#     # Document loading based on file type
#     docs = []
#     for path in file_paths:
#         file_ext = path.lower().split(".")[-1]
        
#         if file_ext == "pdf":
#             loader = PyPDFLoader(path)
#         elif file_ext == "docx":
#             loader = Docx2txtLoader(path)
#         elif file_ext == "txt":
#             loader = TextLoader(path, encoding="utf-8")
#         elif file_ext == "csv":
#             loader = CSVLoader(path)  # Add options as needed
#         elif file_ext in ["xls", "xlsx"]:
#             loader = UnstructuredExcelLoader(path)
#         else:
#             raise ValueError(f"Unsupported file type: {file_ext}")
        
#         docs.extend(loader.load())
    
#     # Chunking
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=200
#     )
#     chunks = text_splitter.split_documents(docs)
    
#     # Vector store creation
#     vectorstore = FAISS.from_documents(
#         chunks, 
#         get_embedding_model()
#     )
    
#     # Save vectorstore locally (optional)
#     vectorstore.save_local("vectorstore")
    
#     # Chain setup
#     memory = ConversationBufferMemory(
#         memory_key="chat_history",
#         return_messages=True
#     )
    
#     retriever = vectorstore.as_retriever(
#         search_type="similarity",
#         search_kwargs={"k": 3}
#     )
    
#     return ConversationalRetrievalChain.from_llm(
#         llm=get_llm(),
#         retriever=retriever,
#         memory=memory
#     )

from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.summarize import load_summarize_chain
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import PyMuPDFLoader,PyPDFLoader, Docx2txtLoader, TextLoader, CSVLoader, UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from models import get_llm, get_embedding_model
import os

def create_rag_chain(file_paths):
    # Note: Cleanup logic has been moved to main.py for session control.
    
    # Document loading based on file type
    docs = []
    for path in file_paths:
        file_ext = os.path.splitext(path)[1].lower()
        
        if file_ext == ".pdf":
            # loader = PyPDFLoader(path)
            loader = PyMuPDFLoader(path)
        elif file_ext == ".docx":
            # loader = Docx2txtLoader(path)
            loader = Docx2txtLoader(path)
        elif file_ext == ".txt":
            loader = TextLoader(path, encoding="utf-8")
        elif file_ext == ".csv":
            loader = CSVLoader(path)
        elif file_ext in [".xls", ".xlsx"]:
            loader = UnstructuredExcelLoader(path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        loaded_docs = loader.load()
        # Add source metadata to each document for better summarization
        for doc in loaded_docs:
            doc.metadata["source"] = os.path.basename(path)
        docs.extend(loaded_docs)
    
    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(docs)
    
    # Vector store creation from all chunks
    vectorstore = FAISS.from_documents(
        chunks, 
        get_embedding_model()
    )
    
    # Save vectorstore locally, overwriting with the new combined data
    vectorstore.save_local("vectorstore")
    
    # Chain setup
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )
    
    chain = ConversationalRetrievalChain.from_llm(
        llm=get_llm(),
        retriever=retriever,
        memory=memory
    )
    
    return chain, docs

def summarize_documents(docs):
    """
    Generates a summary for each unique document source.
    """
    docs_by_source = {}
    for doc in docs:
        source = doc.metadata.get("source", "Unknown")
        if source not in docs_by_source:
            docs_by_source[source] = []
        docs_by_source[source].append(doc)

    llm = get_llm()
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    
    summaries = {}
    for source, source_docs in docs_by_source.items():
        # --> START OF ADDED CODE <--
        # Check if the document list for this source is empty or contains no actual content
        if not source_docs or not any(doc.page_content.strip() for doc in source_docs):
            summaries[source] = "Could not generate summary: No text content could be extracted from this file. It might be a scanned or image-based PDF."
            continue
        # --> END OF ADDED CODE <--
        try:
            summary = chain.run(source_docs)
            summaries[source] = summary
        except Exception as e:
            summaries[source] = f"Could not generate summary due to an error: {e}"
            
    return summaries