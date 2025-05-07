from .base import BaseVectorStore

from pinecone import Pinecone, ServerlessSpec
import os
import numpy as np

def generate_filter_from_tags(tags):
    if not tags:
        return None
    return {
        "tags": {"$in": tags}
    }

class PineconeVectorStore(BaseVectorStore):
    def __init__(self, pinecone_config):
        api_key = os.environ[pinecone_config['api_key_env']]
        self.index_name = pinecone_config['index_name']
        self.dimension = pinecone_config.get('dimension', 384)  # defaulting for MiniLM
        self.metric = pinecone_config.get('metric', 'cosine')
        self.cloud = pinecone_config.get('cloud', 'aws')
        self.region = pinecone_config.get('region', 'us-east-1')

        self.pc = Pinecone(api_key=api_key)

        # Create index if it doesn't exist
        if not self.pc.has_index(self.index_name):
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=ServerlessSpec(cloud=self.cloud, region=self.region)
            )

        self.index = self.pc.Index(self.index_name)

    def save(self, embeddings, texts, metadata=None, ids=None):
        # If IDs are not provided, generate them from the index
        if ids is None:
            ids = [str(i) for i in range(len(embeddings))]
        
        # Prepare the data to upsert
        to_upsert = []
        for i, (embedding, text) in enumerate(zip(embeddings, texts)):
            # Include optional metadata if provided
            entry_metadata = {'text': text}
            if metadata:
                entry_metadata.update(metadata.get(i, {}))  # Merge metadata if exists for this index
            to_upsert.append((ids[i], embedding, entry_metadata))
        
        # Upsert into Pinecone
        self.index.upsert(vectors=to_upsert)


    def load(self):
        # No-op for Pinecone; index is always live
        return self.index

    def retrieve(self, query_embedding, k=3, filter=None):
        query_embedding = np.array(query_embedding).astype("float32").tolist()
        filter = generate_filter_from_tags(filter)
        query_params = {
            "vector": query_embedding,
            "top_k": k,
            "include_metadata": True,
        }
        if filter:
            query_params["filter"] = filter  # Pinecone expects a dict
        # Perform the query and include metadata in the results
        results = results = self.index.query(**query_params)
        # 2. Fallback to unfiltered search if filter returns no results
        if not results:
            print("[INFO] Filtered retrieval returned no results. Falling back to full search.")
            results = vectorstore.retrieve(query_embedding, k=k)
        # Return only the texts from the metadata
        return [
        {
            "id": match['id'],
            "text": match['metadata'].get('text'),
            "metadata": match['metadata'],
            "score": match['score']
        }
        for match in results['matches']
    ]

class PineconeVectorStore_Old:
    def __init__(self, pinecone_config):
        api_key = os.environ[pinecone_config['api_key_env']]
        self.index_name = pinecone_config['index_name']
        self.dimension = pinecone_config.get('dimension', 384)  # defaulting for MiniLM
        self.metric = pinecone_config.get('metric', 'cosine')
        self.cloud = pinecone_config.get('cloud', 'aws')
        self.region = pinecone_config.get('region', 'us-east-1')

        self.pc = Pinecone(api_key=api_key)

        # Create index if it doesn't exist
        if not self.pc.has_index(self.index_name):
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=ServerlessSpec(cloud=self.cloud, region=self.region)
            )

        self.index = self.pc.Index(self.index_name)

    def save(self, embeddings, texts):
        to_upsert = [
            (str(i), embedding, {'text': text})
            for i, (embedding, text) in enumerate(zip(embeddings, texts))
        ]
        self.index.upsert(vectors=to_upsert)

    def load(self):
        # No-op for Pinecone; index is always live
        return self.index

    def retrieve(self, query_embedding, k=3):
        query_embedding = np.array(query_embedding).astype("float32").tolist()
        results = self.index.query(vector=query_embedding, top_k=k, include_metadata=True)
        return [match['metadata']['text'] for match in results['matches']]
