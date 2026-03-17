import pytest
from app.providers.lancedb_provider import LanceDBProvider

def test_lancedb_provider_initialization(tmp_path):
    # Setup
    db_path = tmp_path / "lancedb"
    
    # Action
    provider = LanceDBProvider(uri=str(db_path))
    
    # Assert
    assert provider.uri == str(db_path)
    assert provider.db is not None
    # Check if we can list tables (even if empty) to verify connection is active
    assert provider.db.table_names() == []
