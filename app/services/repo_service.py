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
        structure.append("Repository Root/")
        
        for root, dirs, files in os.walk(path):
            if '.git' in dirs:
                dirs.remove('.git')
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
            
            relative_root = os.path.relpath(root, path)
            if relative_root == ".":
                level = 1
            else:
                level = relative_root.count(os.sep) + 2
            
            indent = ' ' * 4 * level
            if relative_root != ".":
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

    def list_directory(self, repo_path: str, dir_path: str) -> str:
        full_path = os.path.join(repo_path, dir_path)
        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            return f"Error: Directory {dir_path} not found."
        
        items = []
        try:
            for item in sorted(os.listdir(full_path)):
                if item.startswith('.'): continue
                is_dir = os.path.isdir(os.path.join(full_path, item))
                items.append(f"{'[DIR] ' if is_dir else ''}{item}")
            return "\n".join(items) if items else "No files found in this directory."
        except Exception as e:
            return f"Error listing directory {dir_path}: {str(e)}"
