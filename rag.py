# rag.py
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from models import get_llm, get_embedding_model

def create_rag_chain(pdf_docs):
    # Document loading and chunking
    from langchain.document_loaders import PyPDFLoader
    docs = []
    for pdf in pdf_docs:
        loader = PyPDFLoader(pdf)
        docs.extend(loader.load())
    
    # Chunking
    from langchain.text_splitter import RecursiveCharacterTextSplitter
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