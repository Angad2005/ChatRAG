import sys
import traceback

def test_imports():
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

if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)