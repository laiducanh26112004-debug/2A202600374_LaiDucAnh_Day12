from typing import List

from sentence_transformers import CrossEncoder

from retriever import RetrievedChunk


class Reranker:
    """CrossEncoder reranker for candidate chunks."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, candidates: List[RetrievedChunk], top_k: int = 5) -> List[RetrievedChunk]:
        """Score candidates with CrossEncoder and return top_k sorted by score."""
        if not candidates:
            return []

        pairs = [(query, c.chunk.text) for c in candidates]
        scores = self.model.predict(pairs)

        reranked = []
        for candidate, score in zip(candidates, scores):
            reranked.append(
                RetrievedChunk(
                    chunk=candidate.chunk,
                    score=float(score),
                    retrieval_method="reranked",
                )
            )

        reranked.sort(key=lambda x: x.score, reverse=True)
        return reranked[:top_k]