import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.embedder import load_embedder

from src.vectorstore import load_vector_store


def ingest_documents(data_path: str, chunk_size=500, chunk_overlap=100):
    loader = DirectoryLoader(data_path, glob='**/*.txt')
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(documents)

def run_indexing_pipeline(config):

    data_path = os.path.join(os.getcwd(), config['documents']['source_dir'])
    docs = ingest_documents(data_path, chunk_size=500, chunk_overlap=100)
    texts = [doc.page_content for doc in docs]

    embedder_model = load_embedder(config['embedding'])
    embeddings = embedder_model.embed(texts)
    print('Settings for vector store -> ', config['vector_store'])
    vector_store = load_vector_store(config['vector_store'])
    vector_store.save(embeddings, texts)
    print(f"Saved {len(embeddings)} embeddings to vector store.")