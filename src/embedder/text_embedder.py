# src/embedding_loader.py

from sentence_transformers import SentenceTransformer
import openai
import requests


class LocalSentenceTransformerEmbedder:
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts):
        return self.model.encode(texts, show_progress_bar=False)


class OpenAIEmbedder:
    def __init__(self, model_name, api_key):
        openai.api_key = api_key
        self.model = model_name

    def embed(self, texts):
        response = openai.Embedding.create(
            input=texts,
            model=self.model
        )
        return [item['embedding'] for item in response['data']]

class RemoteAPIEmbedder:
    def __init__(self, endpoint_url):
        self.url = endpoint_url

    def embed(self, texts):
        response = requests.post(self.url, json={"texts": texts})
        response.raise_for_status()
        return response.json()["embeddings"]


def load_text_embedder(config: dict):
    provider = config.get("provider")

    if provider == "local":
        return LocalSentenceTransformerEmbedder(config["model_name"])
    
    elif provider == "openai":
        return OpenAIEmbedder(config["model_name"], config["api_key"])
    
    elif provider == "remote_api":
        return RemoteAPIEmbedder(config["endpoint_url"])
    
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")
