from langchain_community.vectorstores import Chroma
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader, TextLoader, CSVLoader, UnstructuredExcelLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import get_llm, get_embedding_model
import os
import requests

from langchain_classic.retrievers.self_query.base import SelfQueryRetriever
from langchain_classic.chains.query_constructor.base import AttributeInfo
from langchain_core.prompts import PromptTemplate

def create_rag_chain(file_paths):
    docs = []
    for path in file_paths:
        file_ext = os.path.splitext(path)[1].lower()
        
        if file_ext == ".pdf":
            loader = PyMuPDFLoader(path)
        elif file_ext == ".docx":
            loader = Docx2txtLoader(path)
        elif file_ext == ".txt":
            loader = TextLoader(path, autodetect_encoding=True)
        elif file_ext == ".csv":
            loader = CSVLoader(path)
        elif file_ext in [".xls", ".xlsx"]:
            loader = UnstructuredExcelLoader(path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        loaded_docs = loader.load()
        for doc in loaded_docs:
            doc.metadata["source"] = os.path.basename(path)
        docs.extend(loaded_docs)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)
    
    vectorstore = Chroma.from_documents(chunks, get_embedding_model())
    
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    metadata_field_info = [
        AttributeInfo(
            name="source",
            description="The filename of the document. Use this when a user asks a question about a specific file.",
            type="string",
        ),
    ]
    document_content_description = "The textual content of a document."
    
    llm = get_llm()
    retriever = SelfQueryRetriever.from_llm(
        llm,
        vectorstore,
        document_content_description,
        metadata_field_info,
        verbose=True
    )
    
    prompt_template = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Do not make up an answer.
    Context: {context}
    Question: {question}
    Answer:"""
    
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": PROMPT}
    )
    
    return chain, docs