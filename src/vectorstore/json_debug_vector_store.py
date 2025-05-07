import json
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class JsonDebugVectorStore:
    def __init__(self, config):
        base_dir = os.getcwd()
        vectorstore_dir = os.path.join(base_dir, config['folder_name'])
        os.makedirs(vectorstore_dir, exist_ok=True)
        print('Vector store_DIR -> ', vectorstore_dir)
        self.index_path = os.path.join(vectorstore_dir, 'json_debug_vs_index.json')
        self.metadata_path  = os.path.join(vectorstore_dir, 'json_debug_vs_metadata.json')


    def save(self, embeddings, texts, metadatas=None, ids=None):
        index_data = []
        metadata_data = {}

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        for i, (embedding, text) in enumerate(zip(embeddings, texts)):
            id_ = ids[i] if ids else str(i)
            index_data.append({
                "id": id_,
                "embedding": embedding.tolist()
            })
            metadata_data[id_] = {
                "text": text,
                "metadata": metadatas[i] if metadatas else {}
            }

        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2)

        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata_data, f, indent=2)


    def load(self):
        if not (os.path.exists(self.index_path) and os.path.exists(self.metadata_path)):
            raise FileNotFoundError("Vectorstore index or metadata file missing.")

        with open(self.index_path, "r", encoding="utf-8") as f:
            index_data = json.load(f)

        with open(self.metadata_path, "r", encoding="utf-8") as f:
            metadata_data = json.load(f)

        self.data = []
        for item in index_data:
            id_ = item["id"]
            embedding = np.array(item["embedding"], dtype=np.float32)
            metadata = metadata_data.get(id_, {})
            self.data.append({
                "id": id_,
                "embedding": embedding,
                "text": metadata.get("text", ""),
                "metadata": metadata.get("metadata", {})
            })

        return self

    def retrieve(self, query_embedding, k=3):
        if not self.data:
            self.load()

        query_vec = np.array(query_embedding).reshape(1, -1)
        matrix = np.array([item["embedding"] for item in self.data])
        scores = cosine_similarity(query_vec, matrix)[0]
        top_k = scores.argsort()[-k:][::-1]

        return [
            {
                "id": self.data[i]["id"],
                "text": self.data[i]["text"],
                "metadata": self.data[i]["metadata"],
                "score": float(scores[i])
            }
            for i in top_k
        ]