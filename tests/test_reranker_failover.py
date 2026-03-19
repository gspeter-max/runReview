import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from app.rag.retrieval.rerank_providers.cloudflare import CloudflareReranker
from app.rag.retrieval.rerank_providers.voyage import VoyageReranker
from app.rag.retrieval.rerank_providers.router import RerankerRouter
from app.rag.retrieval.rerank_providers.base import RerankResult

@pytest.mark.asyncio
async def test_reranker_router_failover():
    # Setup providers
    cloudflare = CloudflareReranker(account_id="fake_cf_id", api_token="fake_cf_token")
    voyage = VoyageReranker(api_key="fake_voyage_key")
    
    router = RerankerRouter(providers=[cloudflare, voyage])
    
    # 1. Mock Cloudflare to throw a 429 Too Many Requests HTTPError
    mock_cf_post = AsyncMock()
    mock_cf_response = MagicMock()
    mock_cf_response.status_code = 429
    mock_cf_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "429 Too Many Requests", request=MagicMock(), response=mock_cf_response
    )
    mock_cf_post.return_value = mock_cf_response

    # 2. Mock Voyage (LiteLLM) to succeed
    mock_voyage_results = MagicMock()
    mock_voyage_results.results = [{"index": 1, "relevance_score": 0.95}]
    
    with patch("httpx.AsyncClient.post", mock_cf_post), \
         patch("litellm.arerank", new_callable=AsyncMock) as mock_litellm:
         
        mock_litellm.return_value = mock_voyage_results
        
        # Act
        results = await router.rerank("test query", ["doc0", "doc1"])
        
        # Assert
        assert len(results) == 1
        assert results[0].index == 1
        assert results[0].score == 0.95
        
        # Verify both providers were called (Cloudflare first, Voyage second)
        mock_cf_post.assert_called_once()
        mock_litellm.assert_called_once()

@pytest.mark.asyncio
async def test_retriever_raises_error_no_providers():
    from app.rag.retrieval.retriever import CodeRetriever
    from app.core.config import settings
    
    # Mock settings to have no keys
    with patch.object(settings, "CLOUDFLARE_API_TOKEN", None), \
         patch.object(settings, "VOYAGE_API_KEY", None):
        
        retriever = CodeRetriever()
        with pytest.raises(RuntimeError) as exc_info:
            await retriever.retrieve_and_rerank("query", ["doc1"])
            
        assert "No reranker providers" in str(exc_info.value)
