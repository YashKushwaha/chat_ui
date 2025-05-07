class BaseVectorStore:
    def save(self, embeddings, texts, metadatas=None, ids=None):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError

    def retrieve(self, query_embedding, k=3, filter=None):
        raise NotImplementedError
    

class BaseVectorStore_old:
    def save(self, embeddings, texts):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError

    def retrieve(self, query_embedding, k, filter=None):
        raise NotImplementedError