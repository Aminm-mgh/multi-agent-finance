import chromadb
from chromadb.config import Settings
from typing import List
from src.retrieval.embedder import Embedder


class VectorStore:
    def __init__(self, collection_name: str = "filings"):
        self.embedder = Embedder()
        self.client = chromadb.PersistentClient(path="chroma_db")
        self.collection = self.client.get_or_create_collection(name=collection_name)


        
    def add_chunks(self, chunks: List[str], metadatas: List[dict], ids: List[str]):
        embeddings = self.embedder.embed(chunks)
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    def clear_collection(self):
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name
        )

    def search(self, query: str, n_results: int = 5) -> dict:
        query_embedding = self.embedder.embed([query])
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        return results