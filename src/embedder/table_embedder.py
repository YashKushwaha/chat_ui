from sentence_transformers import SentenceTransformer
import pandas as pd

class TableEmbedder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, table_path):
        df = pd.read_csv(table_path)
        # Convert entire table to a flat string, row-wise or col-wise
        flattened = df.to_string(index=False)
        return self.model.encode([flattened])


def load_table_embedder(config):
    return TableEmbedder(model_name = 'all-MiniLM-L6-v2')