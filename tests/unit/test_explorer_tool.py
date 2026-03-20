import pytest
import os
import shutil
import tempfile
from app.services.repo_service import RepoService
from app.agents.tools.explorer import execute_list_directory

@pytest.fixture
def temp_repo():
    temp_dir = tempfile.mkdtemp()
    # Create some files and directories
    os.makedirs(os.path.join(temp_dir, "src"))
    os.makedirs(os.path.join(temp_dir, "tests"))
    with open(os.path.join(temp_dir, "README.md"), "w") as f:
        f.write("test")
    with open(os.path.join(temp_dir, "src", "main.py"), "w") as f:
        f.write("print('hello')")
    # Hidden file
    with open(os.path.join(temp_dir, ".env"), "w") as f:
        f.write("SECRET=123")
    
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_repo_service_list_directory(temp_repo):
    service = RepoService()
    
    # Test root listing
    result = service.list_directory(temp_repo, ".")
    assert "README.md" in result
    assert "[DIR] src" in result
    assert "[DIR] tests" in result
    assert ".env" not in result # Should ignore hidden files
    
    # Test subdirectory listing
    result = service.list_directory(temp_repo, "src")
    assert "main.py" in result
    
    # Test non-existent directory
    result = service.list_directory(temp_repo, "nonexistent")
    assert "Error: Directory nonexistent not found." in result

@pytest.mark.asyncio
async def test_execute_list_directory(temp_repo):
    service = RepoService()
    context = {
        "repo_service": service,
        "repo_path": temp_repo
    }
    
    # Test tool execution
    result = await execute_list_directory(context, ".")
    assert "README.md" in result
    assert "[DIR] src" in result
    
    # Test error case
    result = await execute_list_directory(context, "invalid")
    assert "Error: Directory invalid not found." in result
