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




# rag.py
from langchain_community.vectorstores import Chroma 
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import PyMuPDFLoader, Docx2txtLoader, TextLoader, CSVLoader, UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from models import get_llm, get_embedding_model
import os
import requests

from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.prompts import PromptTemplate

MCP_SUMMARY_ENDPOINT = "http://your-mcp-endpoint/summarize"

def create_rag_chain(file_paths):
    docs = []
    for path in file_paths:
        file_ext = os.path.splitext(path)[1].lower()
        
        if file_ext == ".pdf": 
            loader = PyMuPDFLoader(path)
        elif file_ext == ".docx": 
            loader = Docx2txtLoader(path)
        # --> START OF MODIFIED CODE <--
        # Make the TextLoader more robust by auto-detecting the encoding.
        elif file_ext == ".txt": 
            loader = TextLoader(path, autodetect_encoding=True)
        # --> END OF MODIFIED CODE <--
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

# The summarize_documents function does not need any changes.
# def summarize_documents(docs):
#     docs_by_source = {}
#     for doc in docs:
#         source = doc.metadata.get("source", "Unknown")
#         if source not in docs_by_source:
#             docs_by_source[source] = ""
#         docs_by_source[source] += doc.page_content + "\n"

#     payload = {"documents": docs_by_source}

#     try:
#         response = requests.post(MCP_SUMMARY_ENDPOINT, json=payload, timeout=60)
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         raise ConnectionError(
#             f"Could not connect to the summarization service (MCP) at {MCP_SUMMARY_ENDPOINT}."
#         ) from e