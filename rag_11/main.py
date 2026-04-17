import argparse
import sys
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from typing import List, Optional, Dict
from ingestion import IngestionPipeline
from retriever import HybridRetriever, RetrievedChunk, DenseRetriever, SparseRetriever
from reranker import Reranker
from context_builder import ContextBuilder, BuiltContext
from generator import LLMGenerator
from utils import setup_logger, timer
from sentence_transformers import SentenceTransformer

logger = setup_logger("RAGSystem")


@dataclass
class RAGResponse:
    query: str
    answer: str
    context: BuiltContext
    retrieved_count: int
    reranked_count: int


class RAGSystem:
    """Production-ready RAG pipeline powered by Groq."""

    def __init__(
        self,
        index_path: str = "rag_index",
        embed_model: str = "all-MiniLM-L6-v2",
        reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        groq_model: str = "openai/gpt-oss-120b",
        chunk_size: int = 300,
        overlap: int = 50,
        retrieve_top_k: int = 20,
        rerank_top_k: int = 5,
        max_context_tokens: int = 2048,
    ):
        logger.info("Initializing RAG system with Groq backend...")
        self.retrieve_top_k = retrieve_top_k
        self.rerank_top_k = rerank_top_k
        self.embed_model_name = embed_model

        self.pipeline = IngestionPipeline(
            index_path=index_path,
            model_name=embed_model,
            chunk_size=chunk_size,
            overlap=overlap,
        )
        self.retriever = self._build_retriever()
        self.reranker = Reranker(model_name=reranker_model)
        self.context_builder = ContextBuilder(max_tokens=max_context_tokens)
        self.generator = LLMGenerator(model=groq_model)
        logger.info(f"RAG system ready. LLM: {groq_model}")

    def _build_retriever(self) -> Optional[HybridRetriever]:
        corpus, chunks = self.pipeline.get_corpus()
        if not chunks:
            return None  # No data yet

        retriever = HybridRetriever.__new__(HybridRetriever)
        retriever.pipeline = self.pipeline
        model = SentenceTransformer(self.embed_model_name)
        retriever.model = model
        retriever.chunks = chunks
        retriever.dense = DenseRetriever(model, self.pipeline.faiss_index, chunks)
        retriever.sparse = SparseRetriever(corpus, chunks)
        return retriever

    # ------------------------------------------------------------------ #
    #  Ingestion helpers                                                   #
    # ------------------------------------------------------------------ #

    def ingest(self, filepath: str, title: Optional[str] = None) -> int:
        n = len(self.pipeline.ingest_file(filepath, title=title))
        self.retriever = self._build_retriever()
        return n

    def ingest_many(self, filepaths: List[str], skip_existing: bool = True) -> Dict[str, int]:
        """Ingest a list of files, batch-encode in one pass."""
        results = self.pipeline.ingest_files(filepaths, skip_existing=skip_existing)
        self.retriever = self._build_retriever()
        return results

    def ingest_dir(self, directory: str, recursive: bool = False, extensions: Optional[List[str]] = None) -> Dict[str, int]:
        """Ingest all .md/.txt files from a directory."""
        results = self.pipeline.ingest_directory(directory, extensions=extensions, recursive=recursive)
        self.retriever = self._build_retriever()
        return results

    def ingest_glob(self, pattern: str) -> Dict[str, int]:
        """Ingest files matching a glob pattern."""
        results = self.pipeline.ingest_glob(pattern)
        self.retriever = self._build_retriever()
        return results

    def ingest_text(self, text: str, source: str, title: str) -> int:
        n = len(self.pipeline.ingest_text(text, source=source, title=title))
        self.retriever = self._build_retriever()
        return n

    def remove(self, source: str) -> int:
        n = self.pipeline.remove_document(source)
        self.retriever = self._build_retriever()
        return n

    def list_docs(self):
        return self.pipeline.list_documents()

    # ------------------------------------------------------------------ #
    #  Query                                                               #
    # ------------------------------------------------------------------ #

    @timer
    def query(self, question: str) -> RAGResponse:
        if self.retriever is None:
            raise RuntimeError("No documents ingested yet. Run ingest first.")

        logger.info(f"Query: {question}")
        candidates: List[RetrievedChunk] = self.retriever.retrieve(question, top_k=self.retrieve_top_k)
        reranked: List[RetrievedChunk] = self.reranker.rerank(question, candidates, top_k=self.rerank_top_k)
        context: BuiltContext = self.context_builder.build(reranked)
        answer = self.generator.generate_answer(question, context)

        return RAGResponse(
            query=question,
            answer=answer,
            context=context,
            retrieved_count=len(candidates),
            reranked_count=len(reranked),
        )

    def display_response(self, response: RAGResponse) -> None:
        print("\n" + "=" * 60)
        print(f"QUERY: {response.query}")
        print("=" * 60)
        print(f"\nANSWER:\n{response.answer}")
        print("\n" + "-" * 60)
        print(self.context_builder.format_citation_map(response.context.citations))
        print(f"\n[Retrieved: {response.retrieved_count} | Reranked: {response.reranked_count} | Used: {len(response.context.chunks_used)}]")
        print("=" * 60)


# ------------------------------------------------------------------ #
#  CLI                                                                 #
# ------------------------------------------------------------------ #

def main():
    parser = argparse.ArgumentParser(description="RAG System CLI — Groq backend")
    parser.add_argument("--index", default="rag_index")
    parser.add_argument("--model", default="openai/gpt-oss-120b")
    sub = parser.add_subparsers(dest="command")

    # ingest single
    p_ingest = sub.add_parser("ingest", help="Ingest one file")
    p_ingest.add_argument("file")
    p_ingest.add_argument("--title", default=None)

    # ingest many
    p_many = sub.add_parser("ingest-many", help="Ingest multiple files")
    p_many.add_argument("files", nargs="+", help="List of file paths")
    p_many.add_argument("--no-skip", action="store_true", help="Re-ingest existing files")

    # ingest directory
    p_dir = sub.add_parser("ingest-dir", help="Ingest all .md/.txt files in a directory")
    p_dir.add_argument("directory")
    p_dir.add_argument("--recursive", action="store_true")
    p_dir.add_argument("--ext", nargs="+", default=[".md", ".txt"], help="Extensions e.g. .md .txt")
    p_dir.add_argument("--no-skip", action="store_true")

    # ingest glob
    p_glob = sub.add_parser("ingest-glob", help="Ingest files matching a glob pattern")
    p_glob.add_argument("pattern", help='e.g. "docs/**/*.md"')
    p_glob.add_argument("--no-skip", action="store_true")

    # remove
    p_rm = sub.add_parser("remove", help="Remove a document from the index")
    p_rm.add_argument("source", help="Original filepath of the document")

    # list
    sub.add_parser("list", help="List all ingested documents")

    # query
    p_query = sub.add_parser("query", help="Ask a question")
    p_query.add_argument("question")
    p_query.add_argument("--top-k", type=int, default=5)

    args = parser.parse_args()
    rag = RAGSystem(index_path=args.index, groq_model=args.model)

    if args.command == "ingest":
        n = rag.ingest(args.file, title=args.title)
        print(f"✓ Ingested {n} chunks from '{args.file}'")

    elif args.command == "ingest-many":
        results = rag.ingest_many(args.files, skip_existing=not args.no_skip)
        total = sum(results.values())
        print(f"\n✓ Total: {total} chunks across {len([v for v in results.values() if v > 0])} file(s)")

    elif args.command == "ingest-dir":
        results = rag.ingest_dir(args.directory, recursive=args.recursive, extensions=args.ext)
        total = sum(results.values())
        print(f"\n✓ Total: {total} chunks across {len([v for v in results.values() if v > 0])} file(s)")

    elif args.command == "ingest-glob":
        results = rag.ingest_glob(args.pattern)
        total = sum(results.values())
        print(f"\n✓ Total: {total} chunks across {len([v for v in results.values() if v > 0])} file(s)")

    elif args.command == "remove":
        n = rag.remove(args.source)
        print(f"✓ Removed {n} chunks from '{args.source}'")

    elif args.command == "list":
        docs = rag.list_docs()
        if not docs:
            print("No documents ingested.")
        else:
            print(f"\n{'ID':<10} {'Chunks':<8} {'Title':<30} Source")
            print("-" * 80)
            for d in docs:
                print(f"{d['doc_id']:<10} {d['chunks']:<8} {d['title']:<30} {d['source']}")

    elif args.command == "query":
        _, chunks = rag.pipeline.get_corpus()
        if not chunks:
            print("No documents ingested. Run: python main.py ingest-dir <folder>")
            sys.exit(1)
        response = rag.query(args.question)
        rag.display_response(response)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()