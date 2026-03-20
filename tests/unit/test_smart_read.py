import os
import pytest
from app.services.repo_service import RepoService
from app.rag.utils.tokens import truncate_to_tokens, count_tokens

def test_repo_service_read_line_range(tmp_path):
    # Create a dummy file with 10 lines
    file_content = "\n".join([f"Line {i}" for i in range(1, 11)])
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    file_path = repo_dir / "test.txt"
    file_path.write_text(file_content)
    
    service = RepoService()
    
    # Test reading a specific range
    result = service.read_file(str(repo_dir), "test.txt", start_line=3, end_line=5)
    assert "--- [Lines 3-5 of 10] ---" in result
    assert "Line 3" in result
    assert "Line 5" in result
    assert "Line 2" not in result
    assert "Line 6" not in result

    # Test reading with only start_line
    result = service.read_file(str(repo_dir), "test.txt", start_line=8)
    assert "--- [Lines 8-10 of 10] ---" in result
    assert "Line 8" in result
    assert "Line 10" in result
    assert "Line 7" not in result

    # Test reading with only end_line
    result = service.read_file(str(repo_dir), "test.txt", end_line=3)
    assert "--- [Lines 1-3 of 10] ---" in result
    assert "Line 1" in result
    assert "Line 3" in result
    assert "Line 4" not in result

    # Test invalid range
    result = service.read_file(str(repo_dir), "test.txt", start_line=15, end_line=20)
    assert "Error: Invalid range" in result

def test_smart_truncation():
    # Create a long string that will definitely exceed token limit
    long_text = "word " * 10000 
    max_tokens = 100
    
    result = truncate_to_tokens(long_text, max_tokens=max_tokens)
    
    assert "[...TRUNCATED:" in result
    
    # Check if we have both head and tail
    # Since we use 50 tokens for head and 50 for tail
    parts = result.split("[...TRUNCATED:")
    assert len(parts) == 2
    
    head = parts[0].strip()
    tail = parts[1].split("...]\n\n")[1].strip()
    
    assert len(head) > 0
    assert len(tail) > 0
    
    # Verify approximate token count of head and tail
    assert count_tokens(head) <= 50
    assert count_tokens(tail) <= 50

def test_no_truncation_needed():
    short_text = "This is a short text."
    result = truncate_to_tokens(short_text, max_tokens=100)
    assert result == short_text
    assert "[...TRUNCATED:" not in result
