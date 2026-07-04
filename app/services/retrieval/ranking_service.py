import time
import logfire
from flashrank import Ranker, RerankRequest

# Lazy initialization - Ranker is loaded on first use to ensure logfire.configure() has run
_ranker = None


def _get_ranker() -> Ranker:
    """
    Initializes the FlashRank engine lazily. 
    FlashRank uses a local ONNX model (ms-marco-MiniLM-L-6-v2) for ultra-fast reranking.
    """
    global _ranker
    if _ranker is None:
        logfire.info("🧠 Initializing FlashRank Model (TinyBERT) locally...")
        try:
            # We use a specific cache directory to avoid permission issues in production
            _ranker = Ranker(cache_dir="/tmp/flashrank")
        except Exception:
            _ranker = Ranker()
    return _ranker



def rerank_documents(query: str, documents: list[dict | str], top_n: int = 5) -> list[dict]:
    """
    Refines retrieval results by re-scoring documents against the query semantically.

    Why FlashRank?
    Standard vector search (Cosine Similarity) is fast but mathematically "fuzzy."
    FlashRank uses a Cross-Encoder approach which is much more precise but usually slow.
    FlashRank solves this by using highly optimized, quantized ONNX models locally.
    """
    if not documents:
        return []

    normalized_docs = []
    for doc in documents:
        if isinstance(doc, dict):
            normalized_docs.append({
                "content": doc.get("content") or doc.get("text") or "",
                "source": doc.get("source", "Unknown"),
                "source_type": doc.get("source_type", "unknown"),
                "score": doc.get("score"),
            })
        else:
            normalized_docs.append({
                "content": str(doc),
                "source": "Unknown",
                "source_type": "unknown",
                "score": None,
            })

    start_time = time.time()
    logfire.info(f"📡 [Reranker] Sending {len(normalized_docs)} docs to FlashRank Cross-Encoder...")

    try:
        ranker = _get_ranker()

        passages = [
            {"id": i, "text": doc["content"]}
            for i, doc in enumerate(normalized_docs)
        ]

        request = RerankRequest(query=query, passages=passages)
        results = ranker.rerank(request)

        reranked_docs = []
        for res in results[:top_n]:
            doc_id = res.get("id")
            if isinstance(doc_id, int):
                reranked_docs.append(normalized_docs[doc_id])
            else:
                reranked_docs.append(normalized_docs[0])

        duration = time.time() - start_time
        top_score = results[0]['score'] if results else 'N/A'
        logfire.info(f"✅ [Reranker] Done in {duration:.2f}s. Top semantic score: {top_score}")

        return reranked_docs

    except Exception as e:
        logfire.error(f"❌ [Reranker] Semantic Reranking Failed: {e}")
        return normalized_docs[:top_n]