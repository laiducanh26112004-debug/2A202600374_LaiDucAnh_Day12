import os
import json
import glob
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    source: str
    text: str
    embedding: Optional[np.ndarray] = None

    def to_dict(self) -> Dict:
        d = asdict(self)
        d.pop("embedding", None)
        return d


class TextChunker:
    """Split text into overlapping chunks."""

    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> List[str]:
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunks.append(" ".join(words[start:end]))
            if end == len(words):
                break
            start += self.chunk_size - self.overlap
        return chunks


class IngestionPipeline:
    """Ingest multiple markdown/txt files into FAISS index with metadata."""

    def __init__(
        self,
        index_path: str = "rag_index",
        model_name: str = "all-MiniLM-L6-v2",
        chunk_size: int = 300,
        overlap: int = 50,
    ):
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.chunker = TextChunker(chunk_size, overlap)
        self.model = SentenceTransformer(model_name)
        self.chunks: List[Chunk] = []
        self.faiss_index: Optional[faiss.IndexFlatIP] = None
        self._ingested_sources: set = set()

        self._load_existing()

    def _load_existing(self):
        meta_file = self.index_path / "metadata.json"
        faiss_file = self.index_path / "index.faiss"
        if meta_file.exists() and faiss_file.exists():
            with open(meta_file, "r", encoding="utf-8") as f:
                self.chunks = [Chunk(**c) for c in json.load(f)]
            self.faiss_index = faiss.read_index(str(faiss_file))
            self._ingested_sources = {c.source for c in self.chunks}

    def _make_doc_id(self, source: str) -> str:
        return hashlib.md5(source.encode()).hexdigest()[:8]

    def is_ingested(self, source: str) -> bool:
        """Check if a source file has already been ingested."""
        return str(Path(source).resolve()) in self._ingested_sources or source in self._ingested_sources

    # ------------------------------------------------------------------ #
    #  Single file                                                         #
    # ------------------------------------------------------------------ #

    def ingest_file(self, filepath: str, title: Optional[str] = None, skip_existing: bool = True) -> List[Chunk]:
        """Ingest a single .md or .txt file."""
        path = Path(filepath).resolve()

        if skip_existing and self.is_ingested(str(path)):
            print(f"  [skip] already ingested: {path.name}")
            return []

        text = path.read_text(encoding="utf-8")
        return self._ingest_raw(text, source=str(path), title=title or path.stem)

    # ------------------------------------------------------------------ #
    #  Multiple files                                                      #
    # ------------------------------------------------------------------ #

    def ingest_files(
        self,
        filepaths: List[str],
        skip_existing: bool = True,
    ) -> Dict[str, int]:
        """
        Ingest a list of file paths.

        Args:
            filepaths: List of paths to .md or .txt files.
            skip_existing: Skip files already in the index.

        Returns:
            Dict mapping filepath → number of chunks ingested (0 if skipped).
        """
        results: Dict[str, int] = {}
        all_new_chunks: List[Chunk] = []
        all_new_embeddings: List[np.ndarray] = []

        for fp in filepaths:
            path = Path(fp).resolve()
            if not path.exists():
                print(f"  [warn] file not found: {fp}")
                results[fp] = 0
                continue

            if skip_existing and self.is_ingested(str(path)):
                print(f"  [skip] already ingested: {path.name}")
                results[fp] = 0
                continue

            text = path.read_text(encoding="utf-8")
            doc_id = self._make_doc_id(str(path))
            raw_chunks = self.chunker.chunk(text)

            new_chunks = [
                Chunk(
                    chunk_id=f"{doc_id}_{i}",
                    doc_id=doc_id,
                    title=path.stem,
                    source=str(path),
                    text=chunk_text,
                )
                for i, chunk_text in enumerate(raw_chunks)
            ]
            all_new_chunks.extend(new_chunks)
            results[fp] = len(new_chunks)
            print(f"  [queue] {path.name} → {len(new_chunks)} chunks")

        if not all_new_chunks:
            print("Nothing new to ingest.")
            return results

        # Batch encode all new chunks in one pass (fast)
        print(f"\nEmbedding {len(all_new_chunks)} chunks...")
        embeddings = self.model.encode(
            [c.text for c in all_new_chunks],
            normalize_embeddings=True,
            show_progress_bar=True,
            batch_size=64,
        ).astype(np.float32)

        for chunk, emb in zip(all_new_chunks, embeddings):
            chunk.embedding = emb

        self.chunks.extend(all_new_chunks)
        self._ingested_sources.update(c.source for c in all_new_chunks)
        self._rebuild_index()
        self._save()
        return results

    def ingest_directory(
        self,
        directory: str,
        extensions: Optional[List[str]] = None,
        recursive: bool = False,
        skip_existing: bool = True,
    ) -> Dict[str, int]:
        """
        Ingest all matching files from a directory.

        Args:
            directory: Path to folder.
            extensions: File extensions to include, e.g. ['.md', '.txt']. Defaults to both.
            recursive: Whether to recurse into subdirectories.
            skip_existing: Skip already-ingested files.

        Returns:
            Dict mapping filepath → chunks ingested.
        """
        exts = extensions or [".md", ".txt"]
        base = Path(directory)
        if not base.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        pattern = "**/*" if recursive else "*"
        filepaths = [
            str(p) for p in base.glob(pattern)
            if p.is_file() and p.suffix.lower() in exts
        ]
        filepaths.sort()

        print(f"Found {len(filepaths)} file(s) in '{directory}' {exts}")
        return self.ingest_files(filepaths, skip_existing=skip_existing)

    def ingest_glob(
        self,
        pattern: str,
        skip_existing: bool = True,
    ) -> Dict[str, int]:
        """
        Ingest files matching a glob pattern, e.g. 'docs/**/*.md'.

        Args:
            pattern: Glob pattern string.
            skip_existing: Skip already-ingested files.

        Returns:
            Dict mapping filepath → chunks ingested.
        """
        filepaths = sorted(glob.glob(pattern, recursive=True))
        print(f"Glob '{pattern}' matched {len(filepaths)} file(s)")
        return self.ingest_files(filepaths, skip_existing=skip_existing)

    # ------------------------------------------------------------------ #
    #  Remove a document                                                   #
    # ------------------------------------------------------------------ #

    def remove_document(self, source: str) -> int:
        """
        Remove all chunks belonging to a source file and rebuild index.

        Args:
            source: Original filepath string used during ingestion.

        Returns:
            Number of chunks removed.
        """
        resolved = str(Path(source).resolve())
        before = len(self.chunks)
        self.chunks = [
            c for c in self.chunks
            if c.source != source and c.source != resolved
        ]
        removed = before - len(self.chunks)
        if removed:
            self._ingested_sources.discard(source)
            self._ingested_sources.discard(resolved)
            if self.chunks:
                self._rebuild_index()
            else:
                self.faiss_index = None
            self._save()
            print(f"Removed {removed} chunks from '{source}'")
        return removed

    # ------------------------------------------------------------------ #
    #  Internals                                                           #
    # ------------------------------------------------------------------ #

    def _ingest_raw(self, text: str, source: str, title: str) -> List[Chunk]:
        """Encode and store a single document's chunks."""
        doc_id = self._make_doc_id(source)
        raw_chunks = self.chunker.chunk(text)
        new_chunks = [
            Chunk(
                chunk_id=f"{doc_id}_{i}",
                doc_id=doc_id,
                title=title,
                source=source,
                text=chunk_text,
            )
            for i, chunk_text in enumerate(raw_chunks)
        ]
        embeddings = self.model.encode(
            [c.text for c in new_chunks],
            normalize_embeddings=True,
            show_progress_bar=True,
        ).astype(np.float32)
        for chunk, emb in zip(new_chunks, embeddings):
            chunk.embedding = emb

        self.chunks.extend(new_chunks)
        self._ingested_sources.add(source)
        self._rebuild_index()
        self._save()
        return new_chunks

    def ingest_text(self, text: str, source: str, title: str) -> List[Chunk]:
        """Ingest raw text directly (no file)."""
        return self._ingest_raw(text, source=source, title=title)

    def _rebuild_index(self):
        embeddings = np.stack([c.embedding for c in self.chunks]).astype(np.float32)
        dim = embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatIP(dim)
        self.faiss_index.add(embeddings)

    def _save(self):
        meta_file = self.index_path / "metadata.json"
        faiss_file = self.index_path / "index.faiss"
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump([c.to_dict() for c in self.chunks], f, ensure_ascii=False, indent=2)
        faiss.write_index(self.faiss_index, str(faiss_file))

    def list_documents(self) -> List[Dict[str, str]]:
        """Return summary of all ingested documents."""
        seen = {}
        for c in self.chunks:
            if c.doc_id not in seen:
                seen[c.doc_id] = {"doc_id": c.doc_id, "title": c.title, "source": c.source, "chunks": 0}
            seen[c.doc_id]["chunks"] += 1
        return list(seen.values())

    def get_corpus(self) -> Tuple[List[str], List[Chunk]]:
        return [c.text for c in self.chunks], self.chunks