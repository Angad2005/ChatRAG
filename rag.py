# rag.py
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, CSVLoader, UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from models import get_llm, get_embedding_model

def create_rag_chain(file_paths):
    # Document loading based on file type
    docs = []
    for path in file_paths:
        file_ext = path.lower().split(".")[-1]
        
        if file_ext == "pdf":
            loader = PyPDFLoader(path)
        elif file_ext == "docx":
            loader = Docx2txtLoader(path)
        elif file_ext == "txt":
            loader = TextLoader(path, encoding="utf-8")
        elif file_ext == "csv":
            loader = CSVLoader(path)  # Add options as needed
        elif file_ext in ["xls", "xlsx"]:
            loader = UnstructuredExcelLoader(path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        docs.extend(loader.load())
    
    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(docs)
    
    # Vector store creation
    vectorstore = FAISS.from_documents(
        chunks, 
        get_embedding_model()
    )
    
    # Save vectorstore locally (optional)
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
    
    return ConversationalRetrievalChain.from_llm(
        llm=get_llm(),
        retriever=retriever,
        memory=memory
    )