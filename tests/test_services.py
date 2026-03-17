import os
import shutil
import tempfile
from unittest.mock import patch
from app.services.repo_service import RepoService

def test_repo_service_get_file_structure():
    service = RepoService()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a mock directory structure
        os.makedirs(os.path.join(tmpdir, "src"))
        os.makedirs(os.path.join(tmpdir, "tests"))
        os.makedirs(os.path.join(tmpdir, ".git"))
        
        with open(os.path.join(tmpdir, "README.md"), "w") as f:
            f.write("test")
        with open(os.path.join(tmpdir, "src", "main.py"), "w") as f:
            f.write("test")
            
        structure = service.get_file_structure(tmpdir)
        
        # Structure should contain expected files and directories, but ignore .git
        assert ".git/" not in structure
        assert "src/" in structure
        assert "tests/" in structure
        assert "README.md" in structure
        assert "main.py" in structure

def test_repo_service_clone_repo():
    service = RepoService()
    repo_url = "https://github.com/example/repo.git"
    
    with tempfile.TemporaryDirectory() as target_dir:
        # Create a sub-directory to act as target_path so we don't delete the root tempdir
        target_path = os.path.join(target_dir, "repo")
        os.makedirs(target_path)
        dummy_file = os.path.join(target_path, "dummy.txt")
        with open(dummy_file, "w") as f:
            f.write("dummy")
            
        with patch("app.services.repo_service.Repo.clone_from") as mock_clone:
            service.clone_repo(repo_url, target_path)
            
            # The target_path should have been removed by rmtree, and clone_from called.
            assert not os.path.exists(target_path)
            mock_clone.assert_called_once_with(repo_url, target_path)

        # Test clone when path does not exist
        target_path2 = os.path.join(target_dir, "new_repo")
        with patch("app.services.repo_service.Repo.clone_from") as mock_clone:
            service.clone_repo(repo_url, target_path2)
            mock_clone.assert_called_once_with(repo_url, target_path2)
