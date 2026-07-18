try:
    import langchain.chains
    print("langchain.chains found")
except Exception as e:
    print(f"langchain.chains not found: {e}")

try:
    from langchain.chains import ConversationalRetrievalChain
    print("ConversationalRetrievalChain from langchain.chains ok")
except Exception as e:
    print(f"Cannot import ConversationalRetrievalChain from langchain.chains: {e}")

try:
    import langchain_community.chains
    print("langchain_community.chains found")
except Exception as e:
    print(f"langchain_community.chains not found: {e}")

try:
    from langchain_community.chains import ConversationalRetrievalChain
    print("ConversationalRetrievalChain from langchain_community.chains ok")
except Exception as e:
    print(f"Cannot import ConversationalRetrievalChain from langchain_community.chains: {e}")