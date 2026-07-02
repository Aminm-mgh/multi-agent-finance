from sentence_transformers import SentenceTransformer
from typing import List

MODEL_NAME = "all-MiniLM-L6-v2"

class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

    def embed(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist() 