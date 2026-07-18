#!/usr/bin/env python3
"""
Test script to verify the ChatRAG project components work correctly.
"""

import sys
import os
import tempfile

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    modules = [
        'streamlit',
        'os',
        'shutil',
        'requests',
        'rag',
        'models',
        'langchain_community.vectorstores',
        'langchain.chains',
        'langchain.memory',
        'langchain.document_loaders',
        'langchain.text_splitter',
        'langchain.embeddings',
        'langchain.llms',
        'langchain.prompts',
        'langchain.retrievers.self_query.base',
        'langchain.chains.query_constructor.base',
        'transformers',
        'docx',
        'reportlab.lib.pagesizes',
        'reportlab.platypus',
        'reportlab.lib.styles',
        'fastapi',
        'pydantic',
        'io'
    ]
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module}: {e}")
            failed.append((module, str(e)))
    if failed:
        print("\nFailed imports:")
        for module, error in failed:
            print(f"  {module}: {error}")
        return False
    else:
        print("\nAll imports succeeded!")
        return True

def test_models():
    """Test that models module functions can be called (expecting connection errors if LLM server not running)."""
    print("\nTesting models module...")
    try:
        from models import get_llm, get_embedding_model, verify_llm_model_availability
        print("✓ Models module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import models: {e}")
        return False
    
    # Test get_embedding_model (should work without external server)
    try:
        embedding_model = get_embedding_model()
        print("✓ get_embedding_model() created successfully")
    except Exception as e:
        print(f"✗ get_embedding_model() failed: {e}")
        return False
    
    # Test get_llm (will likely fail if LLM server not running, but we expect that)
    try:
        llm = get_llm()
        print("✓ get_llm() created successfully")
    except Exception as e:
        # Check if it's a connection error (expected if server not running)
        if "ConnectionError" in str(e) or "Failed to connect" in str(e) or "Connection refused" in str(e):
            print("⚠ get_llm() created but LLM server not running (expected if server is not started)")
        else:
            print(f"✗ get_llm() failed unexpectedly: {e}")
            return False
    
    # Test verify_llm_model_availability (will likely fail if LLM server not running)
    try:
        # We need an llm client to pass to this function
        llm = get_llm()
        verify_llm_model_availability(llm)
        print("✓ verify_llm_model_availability() succeeded")
    except Exception as e:
        if "ConnectionError" in str(e) or "Failed to connect" in str(e) or "Connection refused" in str(e):
            print("⚠ verify_llm_model_availability() expected connection error (LLM server not running)")
        else:
            print(f"✗ verify_llm_model_availability() failed unexpectedly: {e}")
            return False
    
    return True

def test_rag():
    """Test that rag module functions can be called."""
    print("\nTesting RAG module...")
    try:
        from rag import create_rag_chain, summarize_documents
        print("✓ RAG module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import rag: {e}")
        return False
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document.\nIt has multiple lines.\n")
        temp_file = f.name
    
    try:
        # This will likely fail due to LLM server not running, but we expect that
        rag_chain, docs = create_rag_chain([temp_file])
        print("✓ create_rag_chain() created successfully")
    except Exception as e:
        if "ConnectionError" in str(e) or "Failed to connect" in str(e) or "Connection refused" in str(e):
            print("⚠ create_rag_chain() expected connection error (LLM server not running)")
        else:
            print(f"✗ create_rag_chain() failed unexpectedly: {e}")
            return False
    finally:
        os.unlink(temp_file)
    
    # Test summarize_documents (will also likely fail due to LLM server not running)
    try:
        # We need to create some dummy documents for this test
        from langchain.schema import Document
        dummy_docs = [
            Document(page_content="This is a test document.", metadata={"source": "test.txt"}),
            Document(page_content="Another test document.", metadata={"source": "test2.txt"})
        ]
        summaries = summarize_documents(dummy_docs)
        print("✓ summarize_documents() succeeded")
    except Exception as e:
        if "ConnectionError" in str(e) or "Failed to connect" in str(e) or "Connection refused" in str(e):
            print("⚠ summarize_documents() expected connection error (LLM server not running)")
        else:
            print(f"✗ summarize_documents() failed unexpectedly: {e}")
            return False
    
    return True

def test_mcp():
    """Test that MCP module can be imported and summarizer loaded."""
    print("\nTesting MCP module...")
    try:
        from mcp_main import app, summarizer
        print("✓ MCP module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import MCP module: {e}")
        return False
    
    if summarizer is not None:
        print("✓ MCP summarizer loaded successfully")
    else:
        print("⚠ MCP summarizer is None (model might have failed to load - check internet connection or HF hub)")
        # This is not necessarily a failure, as the model might be loading or cached elsewhere
    
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("ChatRAG Project Test Suite")
    print("=" * 60)
    
    success = True
    success &= test_imports()
    success &= test_models()
    success &= test_rag()
    success &= test_mcp()
    
    print("\n" + "=" * 60)
    if success:
        print("All tests passed! ✓")
        print("\nNote: Some tests expected connection errors if LLM server is not running.")
        print("To fully test the application, please ensure your LLM backend (e.g., LM Studio, Ollama) is running.")
    else:
        print("Some tests failed! ✗")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())