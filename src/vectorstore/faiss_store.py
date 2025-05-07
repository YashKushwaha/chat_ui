import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

from .base import BaseVectorStore

class FAISSVectorStore(BaseVectorStore):
    def __init__(self, faiss_config):
        base_dir = os.getcwd()
        vectorstore_dir = os.path.join(base_dir, faiss_config['folder_name'])
        os.makedirs(vectorstore_dir, exist_ok=True)
        print('Vector store_DIR -> ', vectorstore_dir)
        self.index_path = os.path.join(vectorstore_dir, faiss_config['index_file'])
        self.text_path = os.path.join(vectorstore_dir, faiss_config['texts_file'])

    def save(self, embeddings, texts, metadatas=None, ids=None):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        embeddings = np.array(embeddings).astype("float32")
        dimension = embeddings.shape[1]
        
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)

        faiss.write_index(index, self.index_path)
        print('FAISS index saved to -> ', self.index_path)

        data_bundle = {
            "texts": texts,
            "metadatas": metadatas if metadatas else [None] * len(texts),
            "ids": ids if ids else list(range(len(texts))),
        }

        with open(self.text_path, "wb") as f:
            pickle.dump(data_bundle, f)

    def load(self):
        index = faiss.read_index(self.index_path)

        with open(self.text_path, "rb") as f:
            data_bundle  = pickle.load(f)

        return index, data_bundle 

    def retrieve(self, query_embedding, k=3):
        index, data_bundle = self.load()
        query_embedding = np.array(query_embedding).astype("float32").reshape(1, -1)

        D, I = index.search(query_embedding, k)

        results = []
        for dist, idx in zip(D[0], I[0]):
            results.append({
                "text": data_bundle["texts"][idx],
                "metadata": data_bundle["metadatas"][idx],
                "id": data_bundle["ids"][idx],
                "score": float(dist)  # Lower is better in L2
            })
        return results

# Filtering didn't work, may have to rethink the strategy
class FAISSVectorStoreWithFiltering(FAISSVectorStore):
    def retrieve(self, query_embedding, k=3, filter=None):
        if filter is None:
            print('FAISS store received no filter')
            return super().retrieve(query_embedding, k)

        print('FAISS store received filter -> ', filter)
        index, data_bundle = self.load()
        query_embedding = np.array(query_embedding).astype("float32").reshape(1, -1)

        filtered_indices = self._apply_metadata_filter(data_bundle["metadatas"], filter)
        if not filtered_indices:
            return super().retrieve(query_embedding, k)
        return self._search_and_package(index, query_embedding, data_bundle, filtered_indices, k)
    
    def _apply_metadata_filter(self, metadatas, filter):
        if not filter:
            return list(range(len(metadatas)))

        filtered = []
        for i, metadata in enumerate(metadatas):
            if self._matches_filter(metadata, filter):
                filtered.append(i)
        return filtered
    
    def _matches_filter(self, metadata, filter_tags):
        stored_tags = [tag.lower() for tag in metadata.get("tags", [])]
        query_tags = [tag.lower() for tag in filter_tags]
        return any(tag in stored_tags for tag in query_tags)

    def _matches_filter_old(self, metadata, filter):
        for key, value in filter.items():
            if key not in metadata:
                return False
            if isinstance(value, list):
                if metadata[key] not in value:
                    return False
            else:
                if metadata[key] != value:
                    return False
        return True

    def _search_and_package(self, index, query_embedding, data_bundle, filtered_indices, k):
        filtered_embeddings = np.array([data_bundle["embeddings"][i] for i in filtered_indices]).astype("float32")
        filtered_embeddings = filtered_embeddings.reshape(len(filtered_indices), -1)

        # Use FAISS to search among the filtered embeddings
        from sklearn.metrics.pairwise import euclidean_distances
        distances = euclidean_distances(query_embedding, filtered_embeddings)[0]
        top_k = np.argsort(distances)[:k]

        return [
            {
                "text": data_bundle["texts"][filtered_indices[i]],
                "metadata": data_bundle["metadatas"][filtered_indices[i]],
                "id": data_bundle["ids"][filtered_indices[i]],
                "score": float(distances[i])
            }
            for i in top_k
        ]