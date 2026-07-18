import langchain
print("Langchain version:", langchain.__version__)
print("Attributes:", [attr for attr in dir(langchain) if not attr.startswith('_')])