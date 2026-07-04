from app.services.retrieval import ranking_service


class FakeRanker:
    def rerank(self, request):
        return [{"id": 0, "text": "alpha", "score": 0.95}]


def test_rerank_documents_preserves_metadata(monkeypatch):
    monkeypatch.setattr(ranking_service, "_get_ranker", lambda: FakeRanker())

    documents = [
        {
            "content": "alpha",
            "source": "example.txt",
            "source_type": "true",
        }
    ]

    reranked = ranking_service.rerank_documents("which file", documents, top_n=1)

    assert reranked[0]["content"] == "alpha"
    assert reranked[0]["source"] == "example.txt"
    assert reranked[0]["source_type"] == "true"
