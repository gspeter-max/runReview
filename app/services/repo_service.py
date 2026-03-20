import os
import shutil
from git import Repo

class RepoService:
    def clone_repo(self, repo_url: str, target_path: str):
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        Repo.clone_from(repo_url, target_path)

    def get_file_structure(self, path: str, max_depth: int = 4, max_tokens: int = 4000) -> str:
        """
        Generates a tree-like string of the repository structure.
        max_depth: limit how deep to recurse (None for unlimited)
        max_tokens: rough limit of output length in 'tokens' (1 token ~= 4 chars)
        """
        structure = []
        current_chars = 0
        
        ignored_dirs = {
            '.git', '__pycache__', 'node_modules', 'venv', '.venv', '.pytest_cache', 
            '.ruff_cache', '.mypy_cache', '.github', '.vscode', '.idea', 'build', 'dist'
        }

        for root, dirs, files in os.walk(path):
            relative_root = os.path.relpath(root, path)
            depth = 0 if relative_root == "." else relative_root.count(os.sep) + 1
            
            # Prune directories
            for d in list(dirs):
                if d in ignored_dirs:
                    dirs.remove(d)
            
            if max_depth is not None and depth >= max_depth:
                # If we are at or beyond max_depth, don't recurse further.
                dirs[:] = []
            
            # Show directory name
            if relative_root == ".":
                line = "Project Root/"
            else:
                indent = ' ' * 4 * depth
                line = f"{indent}{os.path.basename(root)}/"
            
            # Check token limit (rough estimate: 4 chars per token)
            if max_tokens and (current_chars + len(line) + 1) // 4 > max_tokens:
                structure.append(f"{' ' * 4 * depth}... (truncated due to token limit)")
                return "\n".join(structure)
            
            structure.append(line)
            current_chars += len(line) + 1
            
            # Show files if we haven't reached depth limit for contents
            if max_depth is None or depth < max_depth:
                sub_indent = ' ' * 4 * (depth + 1)
                for f in files:
                    line = f"{sub_indent}{f}"
                    
                    if max_tokens and (current_chars + len(line) + 1) // 4 > max_tokens:
                        structure.append(f"{sub_indent}... (truncated due to token limit)")
                        return "\n".join(structure)
                    
                    structure.append(line)
                    current_chars += len(line) + 1
        
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

    def read_file(self, repo_path: str, file_path: str, start_line: int = None, end_line: int = None) -> str:
        import os
        full_path = os.path.join(repo_path, file_path)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                if start_line is not None or end_line is not None:
                    lines = f.readlines()
                    total_lines = len(lines)
                    
                    # Default values for missing range ends
                    start = max(1, start_line) if start_line is not None else 1
                    end = min(total_lines, end_line) if end_line is not None else total_lines
                    
                    if start > total_lines or start > end:
                        return f"Error: Invalid range {start}-{end} for file with {total_lines} lines."
                    
                    # slice is 0-indexed, end is inclusive in our API but exclusive in slice
                    selected_lines = lines[start-1:end]
                    content = "".join(selected_lines)
                    return f"--- [Lines {start}-{end} of {total_lines}] ---\n{content}"
                
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
