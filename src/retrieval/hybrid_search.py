from rank_bm25 import BM25Okapi
from typing import List, Tuple
from src.retrieval.vector_store import VectorStore

class HybridSearch:
    def __init__(self):
        self.vector_store = VectorStore()
        self.chunks: List[str] = []
        self.metadatas: List[dict] = []
        self.bm25 = None

    def add_chunks(self, chunks: List[str], metadatas: List[dict], ids: List[str]):
        self.chunks = chunks
        self.metadatas = metadatas
        self.vector_store.add_chunks(chunks, metadatas, ids)
        tokenized = [chunk.lower().split() for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized)



    def search(self, query: str, n_results: int = 5) -> List[dict]:
        # Vector search
        vector_results = self.vector_store.search(query, n_results=n_results)
        vector_docs = vector_results['documents'][0]

        # BM25 keyword search
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        top_bm25_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:n_results]
        bm25_docs = [self.chunks[i] for i in top_bm25_indices]

        # Combine results (Reciprocal Rank Fusion)
        all_docs = list(set(vector_docs + bm25_docs))
        
        results = []
        for doc in all_docs:
            idx = self.chunks.index(doc)
            results.append({
                "text": doc,
                "metadata": self.metadatas[idx]
            })
        
        return results