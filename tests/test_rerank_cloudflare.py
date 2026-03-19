import pytest
from unittest.mock import patch
from app.rag.retrieval.rerank_providers.cloudflare import CloudflareReranker

@pytest.mark.asyncio
async def test_cloudflare_rerank_success():
    mock_response = {
        "success": True,
        "result": [{"index": 0, "score": 0.9}, {"index": 1, "score": 0.1}]
    }
    with patch("httpx.AsyncClient.post") as mock_post:
        # We need mock_post.return_value to act as an async context manager
        # because the code uses `async with httpx.AsyncClient() as client: client.post(...)`
        # Wait, the code in the plan uses:
        # async with httpx.AsyncClient() as client:
        #     resp = await client.post(...)
        # So client.post is an async method returning a response.
        mock_post.return_value.json = lambda: mock_response
        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status = lambda: None
        
        provider = CloudflareReranker(account_id="test_id", api_token="test_token")
        results = await provider.rerank("query", ["doc1", "doc2"])
        
        assert len(results) == 2
        assert results[0].score == 0.9
