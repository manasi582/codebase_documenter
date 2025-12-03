import os
from typing import List, Dict
from pathlib import Path


class FileAnalyzer:
    """Service for analyzing file system structure."""
    
    # Directories to ignore
    IGNORE_DIRS = {
        '.git', '.svn', '.hg',
        'node_modules', 'venv', 'env', '.venv', '__pycache__',
        'dist', 'build', 'out', '.next',
        'coverage', '.pytest_cache', '.mypy_cache',
        'vendor', 'target', 'bin', 'obj'
    }
    
    # File extensions to ignore
    IGNORE_EXTENSIONS = {
        '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib',
        '.class', '.o', '.a', '.lib', '.exe',
        '.log', '.lock', '.swp', '.swo',
        '.jpg', '.jpeg', '.png', '.gif', '.ico', '.svg',
        '.mp4', '.avi', '.mov', '.mp3', '.wav',
        '.zip', '.tar', '.gz', '.rar', '.7z'
    }
    
    # Code file extensions to prioritize
    CODE_EXTENSIONS = {
        '.py', '.js', '.jsx', '.ts', '.tsx',
        '.java', '.cpp', '.c', '.h', '.hpp',
        '.go', '.rs', '.rb', '.php',
        '.cs', '.swift', '.kt', '.scala',
        '.sh', '.bash', '.zsh',
        '.sql', '.graphql',
        '.html', '.css', '.scss', '.sass',
        '.json', '.yaml', '.yml', '.toml', '.xml',
        '.md', '.rst', '.txt'
    }
    
    @classmethod
    def analyze_repository(cls, repo_path: str) -> Dict:
        """
        Analyze repository structure and return metadata.
        
        Returns:
            Dictionary containing:
            - total_files: Total number of files
            - code_files: List of code file paths
            - directories: List of directories
            - file_tree: Hierarchical structure
        """
        code_files = []
        directories = []
        total_files = 0
        
        for root, dirs, files in os.walk(repo_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in cls.IGNORE_DIRS]
            
            # Get relative path from repo root
            rel_root = os.path.relpath(root, repo_path)
            if rel_root != '.':
                directories.append(rel_root)
            
            for file in files:
                total_files += 1
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                
                # Check if it's a code file
                ext = os.path.splitext(file)[1].lower()
                if ext in cls.CODE_EXTENSIONS and ext not in cls.IGNORE_EXTENSIONS:
                    code_files.append({
                        'path': rel_path,
                        'full_path': file_path,
                        'extension': ext,
                        'size': os.path.getsize(file_path)
                    })
        
        return {
            'total_files': total_files,
            'code_files': code_files,
            'directories': sorted(directories),
            'code_file_count': len(code_files)
        }
    
    @classmethod
    def get_file_content(cls, file_path: str, max_size: int = 1_000_000) -> str:
        """
        Read file content safely.
        
        Args:
            file_path: Path to file
            max_size: Maximum file size to read (default: 1MB)
            
        Returns:
            File content as string
        """
        try:
            file_size = os.path.getsize(file_path)
            if file_size > max_size:
                return f"[File too large: {file_size} bytes]"
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            return f"[Error reading file: {str(e)}]"
    
    @classmethod
    def group_files_by_directory(cls, code_files: List[Dict]) -> Dict[str, List[Dict]]:
        """Group code files by their directory."""
        grouped = {}
        for file_info in code_files:
            directory = os.path.dirname(file_info['path']) or '.'
            if directory not in grouped:
                grouped[directory] = []
            grouped[directory].append(file_info)
        return grouped
