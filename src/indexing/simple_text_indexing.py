import os
import logging
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from .base_indexer import BaseIndexer

from src.embedder import load_text_embedder

from src.vectorstore import load_vector_store

from src.logger_config import setup_logger
logger = setup_logger(__name__)

class SimpleTextIndexer(BaseIndexer):
    def __init__(self, config):
        self.config=config
        self.docs = None

    def ingest(self):
        data_path = os.path.join(os.getcwd(), self.config['documents']['source_dir'])
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Directory not found: {data_path}")

        loader = DirectoryLoader(data_path, glob='**/*.txt')
        documents = loader.load()

        chunk_size = self.config['chunking_strategy']['chunk_size']
        chunk_overlap = self.config['chunking_strategy']['chunk_overlap']
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        split_docs = splitter.split_documents(documents)
        self.docs = splitter.split_documents(documents)
        logger.info(f"Ingested and split {len(split_docs)} document chunks.")
        return split_docs

    def index(self):
        if self.docs is None:
            logger.debug("No preloaded docs found, ingesting now...")
            self.ingest()
        texts = [doc.page_content for doc in self.docs]

        embedder_model = load_text_embedder(self.config['embedding'])
        embeddings = embedder_model.embed(texts)

        vector_store = load_vector_store(self.config['vector_store'])
        vector_store.save(embeddings, texts)

        logger.info(f"Saved {len(embeddings)} embeddings to vector store.")
