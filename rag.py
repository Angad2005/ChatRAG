# rag.py
import os
from models import get_llm, get_embedding_model
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain_community.vectorstores import FAISS
# V V V IMPORTED THE NEW, CORRECT LOADER V V V
from langchain_unstructured import UnstructuredLoader
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

def load_documents(file_paths):
    """
    Loads documents using the powerful UnstructuredLoader, which will
    intelligently apply OCR and other strategies as needed.
    """
    docs = []
    for path in file_paths:
        try:
            # Use the new UnstructuredLoader
            loader = UnstructuredLoader(path, mode="single", strategy="auto")
            docs.extend(loader.load())
        except Exception as e:
            print(f"Error loading document {path}: {e}")
    return docs

def create_rag_chain(file_paths):
    """Creates a modern, history-aware RAG chain from a list of file paths."""
    llm = get_llm()
    
    docs = load_documents(file_paths)
    if not docs: return None
        
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    if not splits: return None

    try:
        vectorstore = FAISS.from_documents(documents=splits, embedding=get_embedding_model())
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    except Exception as e:
        print(f"Error creating FAISS vector store: {e}")
        return None

    contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given a chat history and the latest user question which might reference context in the chat history, formulate a standalone question which can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

    qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.\n\n{context}"),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
    Youtube_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, Youtube_chain)
    return rag_chain

def _parse_llm_response(text: str) -> str:
    """Parses the LLM response to remove special tokens."""
    marker = "final<|message|>".strip()
    if marker in text:
        return text.split(marker, 1)[1].strip()
    return text.strip()

def create_web_search_chain():
    """Creates a chain that gets context from the web and answers questions."""
    llm = get_llm()
    search_tool = DuckDuckGoSearchRun()

    prompt = ChatPromptTemplate.from_template(
        "You are a helpful research assistant. Answer the following question based ONLY on the provided web search context.\n\n"
        "CONTEXT:\n{context}\n\n"
        "QUESTION:\n{question}"
    )

    chain = (
        RunnablePassthrough.assign(context=(lambda x: search_tool.run(x["question"])))
        | prompt
        | llm
        | StrOutputParser()
        | RunnableLambda(_parse_llm_response)
    )
    return chain
