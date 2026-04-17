from typing import List, Tuple, Dict, Any
from dataclasses import dataclass

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

from ingestion import Chunk, IngestionPipeline


@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float
    retrieval_method: str


class DenseRetriever:
    """FAISS-based dense retrieval."""

    def __init__(self, model: SentenceTransformer, index: faiss.Index, chunks: List[Chunk]):
        self.model = model
        self.index = index
        self.chunks = chunks

    def retrieve(self, query: str, top_k: int = 10) -> List[RetrievedChunk]:
        query_emb = self.model.encode(
            [query], normalize_embeddings=True
        ).astype(np.float32)
        scores, indices = self.index.search(query_emb, top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            results.append(
                RetrievedChunk(
                    chunk=self.chunks[idx],
                    score=float(score),
                    retrieval_method="dense",
                )
            )
        return results


class SparseRetriever:
    """BM25-based sparse retrieval."""

    def __init__(self, corpus: List[str], chunks: List[Chunk]):
        tokenized = [doc.lower().split() for doc in corpus]
        self.bm25 = BM25Okapi(tokenized)
        self.chunks = chunks

    def retrieve(self, query: str, top_k: int = 10) -> List[RetrievedChunk]:
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            if scores[idx] <= 0:
                continue
            results.append(
                RetrievedChunk(
                    chunk=self.chunks[idx],
                    score=float(scores[idx]),
                    retrieval_method="sparse",
                )
            )
        return results


class HybridRetriever:
    """Merge dense + sparse results with deduplication."""

    def __init__(self, pipeline: IngestionPipeline, model_name: str = "all-MiniLM-L6-v2"):
        self.pipeline = pipeline
        self.model = SentenceTransformer(model_name)
        corpus, chunks = pipeline.get_corpus()
        self.chunks = chunks
        self.dense = DenseRetriever(self.model, pipeline.faiss_index, chunks)
        self.sparse = SparseRetriever(corpus, chunks)

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        dense_weight: float = 0.6,
        sparse_weight: float = 0.4,
    ) -> List[RetrievedChunk]:
        dense_results = self.dense.retrieve(query, top_k=top_k)
        sparse_results = self.sparse.retrieve(query, top_k=top_k)

        scores: Dict[str, float] = {}
        chunk_map: Dict[str, Chunk] = {}

        max_dense = max((r.score for r in dense_results), default=1.0)
        max_sparse = max((r.score for r in sparse_results), default=1.0)

        for r in dense_results:
            cid = r.chunk.chunk_id
            scores[cid] = scores.get(cid, 0.0) + dense_weight * (r.score / max_dense)
            chunk_map[cid] = r.chunk

        for r in sparse_results:
            cid = r.chunk.chunk_id
            scores[cid] = scores.get(cid, 0.0) + sparse_weight * (r.score / max_sparse)
            chunk_map[cid] = r.chunk

        sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)[:top_k]
        return [
            RetrievedChunk(chunk=chunk_map[cid], score=scores[cid], retrieval_method="hybrid")
            for cid in sorted_ids
        ]