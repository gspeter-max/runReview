import os
import shutil
from git import Repo

class RepoService:
    def clone_repo(self, repo_url: str, target_path: str):
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        Repo.clone_from(repo_url, target_path)

    def get_file_structure(self, path: str) -> str:
        structure = []
        for root, dirs, files in os.walk(path):
            if '.git' in dirs:
                dirs.remove('.git')
            level = root.replace(path, '').count(os.sep)
            indent = ' ' * 4 * level
            structure.append(f"{indent}{os.path.basename(root)}/")
            sub_indent = ' ' * 4 * (level + 1)
            for f in files:
                structure.append(f"{sub_indent}{f}")
        return "\n".join(structure)
