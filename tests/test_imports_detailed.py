#!/usr/bin/env python3
"""
Test the imports in the current environment.
"""

def test_import(module_name, fromlist=None):
    try:
        if fromlist:
            __import__(module_name, fromlist=fromlist)
        else:
            __import__(module_name)
        return True
    except Exception as e:
        return False, e

# Test the imports from models.py
print("Testing models.py imports:")
success, err = test_import('langchain.llms')
if not success:
    print(f"  FAIL: langchain.llms - {err}")
else:
    print("  PASS: langchain.llms")

success, err = test_import('langchain.embeddings')
if not success:
    print(f"  FAIL: langchain.embeddings - {err}")
else:
    print("  PASS: langchain.embeddings")

# Test the imports from rag.py
print("\nTesting rag.py imports:")
success, err = test_import('langchain_community.vectorstores')
if not success:
    print(f"  FAIL: langchain_community.vectorstores - {err}")
else:
    print("  PASS: langchain_community.vectorstores")

success, err = test_import('langchain.chains')
if not success:
    print(f"  FAIL: langchain.chains - {err}")
else:
    print("  PASS: langchain.chains")

success, err = test_import('langchain.memory')
if not success:
    print(f"  FAIL: langchain.memory - {err}")
else:
    print("  PASS: langchain.memory")

success, err = test_import('langchain.document_loaders')
if not success:
    print(f"  FAIL: langchain.document_loaders - {err}")
else:
    print("  PASS: langchain.document_loaders")

success, err = test_import('langchain.text_splitter')
if not success:
    print(f"  FAIL: langchain.text_splitter - {err}")
else:
    print("  PASS: langchain.text_splitter")

# Also test the specific submodules
print("\nTesting specific submodules:")
success, err = test_import('langchain.chains.question_constructor')
if not success:
    print(f"  FAIL: langchain.chains.question_constructor - {err}")
else:
    print("  PASS: langchain.chains.question_constructor")

print("\nDone.")