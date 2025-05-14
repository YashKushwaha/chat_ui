from langchain.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://en.wikipedia.org/wiki/OpenAI")
docs = loader.load()


print(docs)