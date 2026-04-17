from typing import List, Tuple, Dict
from dataclasses import dataclass

from retriever import RetrievedChunk


@dataclass
class BuiltContext:
    formatted_text: str
    citations: Dict[int, Dict[str, str]]
    chunks_used: List[RetrievedChunk]


class ContextBuilder:
    """Build citation-indexed context from reranked chunks."""

    def __init__(self, max_tokens: int = 2048, chars_per_token: float = 4.0):
        self.max_tokens = max_tokens
        self.max_chars = int(max_tokens * chars_per_token)

    def build(self, ranked_chunks: List[RetrievedChunk]) -> BuiltContext:
        """
        Select top chunks within token budget and format with citation indices.

        Returns BuiltContext with formatted text and citation mapping.
        """
        selected: List[RetrievedChunk] = []
        total_chars = 0

        for rc in ranked_chunks:
            chunk_chars = len(rc.chunk.text)
            if total_chars + chunk_chars > self.max_chars:
                remaining = self.max_chars - total_chars
                if remaining > 100:
                    truncated_text = rc.chunk.text[:remaining]
                    from copy import deepcopy
                    from ingestion import Chunk
                    truncated_chunk = deepcopy(rc)
                    truncated_chunk.chunk = Chunk(
                        chunk_id=rc.chunk.chunk_id,
                        doc_id=rc.chunk.doc_id,
                        title=rc.chunk.title,
                        source=rc.chunk.source,
                        text=truncated_text,
                    )
                    selected.append(truncated_chunk)
                break
            selected.append(rc)
            total_chars += chunk_chars

        lines = []
        citations: Dict[int, Dict[str, str]] = {}
        for i, rc in enumerate(selected, start=1):
            lines.append(f"[{i}] {rc.chunk.text}")
            citations[i] = {
                "chunk_id": rc.chunk.chunk_id,
                "doc_id": rc.chunk.doc_id,
                "title": rc.chunk.title,
                "source": rc.chunk.source,
                "score": str(round(rc.score, 4)),
            }

        return BuiltContext(
            formatted_text="\n\n".join(lines),
            citations=citations,
            chunks_used=selected,
        )

    def format_citation_map(self, citations: Dict[int, Dict[str, str]]) -> str:
        lines = ["**Sources:**"]
        for idx, meta in citations.items():
            lines.append(f"  [{idx}] {meta['title']} — {meta['source']}")
        return "\n".join(lines)