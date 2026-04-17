"""
api_server.py — Flask bridge between EduBot frontend and RAG backend.
Run: python api_server.py
"""

import os
import sys
from pathlib import Path
from flask_cors import CORS
from flask import Flask, request, jsonify, send_from_directory

# ── Add rag_system to path if needed ──────────────────────────────────────
RAG_DIR = os.environ.get("RAG_DIR", ".")
sys.path.insert(0, RAG_DIR)

from ingestion import IngestionPipeline
from retriever import HybridRetriever, DenseRetriever, SparseRetriever
from reranker import Reranker
from context_builder import ContextBuilder
from generator import LLMGenerator
from utils import setup_logger
from sentence_transformers import SentenceTransformer

logger = setup_logger("API")
FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def static_files(path):
    if path.startswith("api"):
        return jsonify({"error": "not found"}), 404
    return send_from_directory(FRONTEND_DIR, path)
  # Allow frontend on any origin during dev

# ── Globals ────────────────────────────────────────────────────────────────
INDEX_PATH   = os.environ.get("RAG_INDEX", "rag_index")
EMBED_MODEL  = "all-MiniLM-L6-v2"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
GROQ_MODEL   = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

pipeline      = None
retriever     = None
reranker      = None
ctx_builder   = None
generator     = None


def _build_retriever(embed_model_name: str):
    corpus, chunks = pipeline.get_corpus()
    if not chunks:
        return None
    ret = HybridRetriever.__new__(HybridRetriever)
    ret.pipeline = pipeline
    model = SentenceTransformer(embed_model_name)
    ret.model   = model
    ret.chunks  = chunks
    ret.dense   = DenseRetriever(model, pipeline.faiss_index, chunks)
    ret.sparse  = SparseRetriever(corpus, chunks)
    return ret


def init_rag():
    global pipeline, retriever, reranker, ctx_builder, generator
    logger.info("Loading RAG components…")
    pipeline    = IngestionPipeline(index_path=INDEX_PATH, model_name=EMBED_MODEL)
    retriever   = _build_retriever(EMBED_MODEL)
    reranker    = Reranker(model_name=RERANK_MODEL)
    ctx_builder = ContextBuilder(max_tokens=2048)
    generator   = LLMGenerator(model=GROQ_MODEL)
    logger.info("RAG ready.")


# ── Routes ─────────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    _, chunks = pipeline.get_corpus()
    return jsonify({"status": "ok", "chunks": len(chunks)})


@app.route("/api/docs", methods=["GET"])
def list_docs():
    docs = pipeline.list_documents()
    return jsonify({"documents": docs})


@app.route("/api/ingest", methods=["POST"])
def ingest():
    """
    Body (JSON):
      { "directory": "path/to/docs" }          — ingest whole folder
      { "files": ["a.md", "b.md"] }            — ingest list of files
      { "text": "...", "source": "x", "title": "y" }  — ingest raw text
    """
    global retriever
    data = request.get_json(force=True)

    if "directory" in data:
        recursive = data.get("recursive", False)
        results   = pipeline.ingest_directory(data["directory"], recursive=recursive)
    elif "files" in data:
        results = pipeline.ingest_files(data["files"])
    elif "text" in data:
        chunks  = pipeline.ingest_text(data["text"], data.get("source","raw"), data.get("title","Untitled"))
        results = {data.get("source","raw"): len(chunks)}
    else:
        return jsonify({"error": "Provide 'directory', 'files', or 'text'"}), 400

    retriever = _build_retriever(EMBED_MODEL)
    total     = sum(results.values())
    return jsonify({"ingested_chunks": total, "details": results})


@app.route("/api/query", methods=["POST"])
def query():
    """
    Body: { "question": "...", "top_k": 5 }
    Returns:
      {
        "answer":    "...",
        "citations": { "1": {"title":..., "source":...}, ... },
        "confidence": "high" | "low",
        "chunks_used": 3
      }
    """
    if retriever is None:
        return jsonify({
            "answer": "Chưa có tài liệu nào được nạp vào hệ thống. Vui lòng ingest tài liệu trước.",
            "citations": {},
            "confidence": "low",
            "chunks_used": 0
        }), 200

    data     = request.get_json(force=True)
    question = data.get("question", "").strip()
    top_k    = int(data.get("top_k", 5))

    if not question:
        return jsonify({"error": "question is required"}), 400

    # Retrieve → Rerank → Build context → Generate
    candidates = retriever.retrieve(question, top_k=top_k * 4)
    reranked   = reranker.rerank(question, candidates, top_k=top_k)
    context    = ctx_builder.build(reranked)
    answer     = generator.generate_answer(question, context)

    # Confidence heuristic: if top reranker score < threshold → low
    confidence = "high"
    if reranked and reranked[0].score < 0.5:
        confidence = "low"
    if not reranked:
        confidence = "low"

    return jsonify({
        "answer":      answer,
        "citations":   context.citations,
        "confidence":  confidence,
        "chunks_used": len(context.chunks_used),
    })


@app.route("/api/remove", methods=["DELETE"])
def remove():
    global retriever
    data   = request.get_json(force=True)
    source = data.get("source", "")
    if not source:
        return jsonify({"error": "source required"}), 400
    n         = pipeline.remove_document(source)
    retriever = _build_retriever(EMBED_MODEL)
    return jsonify({"removed_chunks": n})


# ── Entry ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_rag()
    app.run(host="0.0.0.0", port=5000, debug=False)
