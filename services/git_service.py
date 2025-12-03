import os
import shutil
import tempfile
from typing import Optional
from git import Repo, GitCommandError
import re


class GitService:
    """Service for handling Git repository operations."""
    
    TEMP_DIR = "/tmp/repos"
    
    @staticmethod
    def validate_github_url(url: str) -> bool:
        """Validate if the URL is a valid GitHub repository URL."""
        patterns = [
            r"^https://github\.com/[\w-]+/[\w.-]+/?$",
            r"^git@github\.com:[\w-]+/[\w.-]+\.git$",
        ]
        return any(re.match(pattern, url.strip()) for pattern in patterns)
    
    @staticmethod
    def extract_repo_name(url: str) -> str:
        """Extract repository name from GitHub URL."""
        # Remove .git suffix if present
        url = url.rstrip("/").replace(".git", "")
        # Extract owner/repo from URL
        match = re.search(r"github\.com[:/]([\w-]+/[\w.-]+)", url)
        if match:
            return match.group(1).replace("/", "_")
        return "unknown_repo"
    
    @classmethod
    def clone_repository(cls, github_url: str) -> tuple[str, str]:
        """
        Clone a GitHub repository to a temporary directory.
        
        Returns:
            tuple: (repo_path, repo_name)
        """
        if not cls.validate_github_url(github_url):
            raise ValueError(f"Invalid GitHub URL: {github_url}")
        
        # Create temp directory if it doesn't exist
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        
        # Generate unique directory name
        repo_name = cls.extract_repo_name(github_url)
        repo_path = os.path.join(cls.TEMP_DIR, f"{repo_name}_{os.urandom(4).hex()}")
        
        try:
            # Clone the repository
            Repo.clone_from(github_url, repo_path, depth=1)
            return repo_path, repo_name
        except GitCommandError as e:
            # Clean up on failure
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    @staticmethod
    def cleanup_repository(repo_path: str) -> None:
        """Remove cloned repository directory."""
        if os.path.exists(repo_path):
            try:
                shutil.rmtree(repo_path)
            except Exception as e:
                print(f"Warning: Failed to cleanup repository at {repo_path}: {e}")
