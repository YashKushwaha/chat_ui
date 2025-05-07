# src/retriever.py

from typing import Any, List
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# FAISS-specific imports
import faiss
import pickle
import os

class LocalFaissRetriever:
    def __init__(self, index_path: str, texts_path: str, embedder: Any):
        self.index = faiss.read_index(index_path)
        with open(texts_path, "rb") as f:
            self.texts = pickle.load(f)
        self.embedder = embedder

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        query_embedding = np.array([self.embedder.embed_query(query)], dtype=np.float32)
        _, indices = self.index.search(query_embedding, top_k)
        return [self.texts[i] for i in indices[0]]


def load_retriever(config: dict, embedder: Any):
    """Load appropriate retriever based on config"""

    store_type = config["type"]
    if store_type == "faiss":
        #db_location = os.path.join(os.getcwd(),config["faiss"]['folder_name'])
        db_location = os.path.join(os.getcwd(),'')
        os.makedirs(db_location, exist_ok=True)

        index_path=os.path.join(db_location,config["faiss"]["index_file"])
        texts_path=os.path.join(db_location,config["faiss"]["texts_file"])
        print('expected faisss location',index_path, texts_path)

        return LocalFaissRetriever(
            index_path=index_path,
            texts_path=texts_path,
            embedder=embedder,
        )
    elif store_type == "pinecone":
        # You could implement and return a PineconeRetriever here
        raise NotImplementedError("Pinecone support not yet implemented")
    else:
        raise ValueError(f"Unsupported vector store type: {store_type}")
