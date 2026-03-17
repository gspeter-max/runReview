import pytest
from app.providers.lancedb_provider import LanceDBProvider
import os

def test_lancedb_hybrid_search(tmp_path):
    # Setup
    db_path = tmp_path / "lancedb"
    provider = LanceDBProvider(uri=str(db_path))
    
    table_name = "test_table"
    documents = [
        {"id": 1, "vector": [0.1, 0.2], "text": "Python code analysis"},
        {"id": 2, "vector": [0.8, 0.9], "text": "Rust performance check"},
        {"id": 3, "vector": [0.2, 0.1], "text": "Java security review"}
    ]
    
    # Create table and add documents
    # These methods don't exist yet, so this will fail
    provider.create_table(table_name, schema=None, data=documents)
    
    # Perform hybrid search for 'Rust'
    # We expect the Rust document (id=2) to be the top result
    results = provider.search(table_name, query_vector=[0.8, 0.9], query_text="Rust", limit=1)
    
    assert len(results) > 0
    assert results[0]["id"] == 2
    assert "Rust" in results[0]["text"]
