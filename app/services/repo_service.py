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

    def read_files_content(self, repo_path: str, file_list: list) -> str:
        content = []
        for file in file_list:
            file_path = os.path.join(repo_path, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                content.append(f"--- File: {file} ---\n{file_content}\n")
            except Exception:
                pass
        return "\n".join(content)

    def read_file(self, repo_path: str, file_path: str) -> str:
        import os
        full_path = os.path.join(repo_path, file_path)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        return f"Error: File {file_path} not found."
