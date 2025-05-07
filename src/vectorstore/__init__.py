#from .faiss_store import save_embeddings, load_embeddings  # or dynamically select based on config

from .faiss_store import FAISSVectorStore, FAISSVectorStoreWithFiltering
from .pinecone_store import PineconeVectorStore
from .json_debug_vector_store import JsonDebugVectorStore

def load_vector_store(config):
    vector_store_to_use = config['vector_store_to_use']
    if vector_store_to_use == 'faiss':
        vector_store = FAISSVectorStore(config[vector_store_to_use])
    elif vector_store_to_use == 'faiss_with_filtering':
        vector_store = FAISSVectorStoreWithFiltering(config[vector_store_to_use])        
    elif vector_store_to_use == 'pinecone':
        vector_store = PineconeVectorStore(config[vector_store_to_use])
    elif vector_store_to_use == 'json_debug':
        return JsonDebugVectorStore(config[vector_store_to_use])
    else:
        raise ValueError(f"Unsupported vectorstore: {vector_store_to_use}")
    return vector_store