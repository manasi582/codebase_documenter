"""Local file storage service as alternative to S3."""
import os
import shutil
import json
from pathlib import Path


class LocalStorageService:
    """Service for handling local file storage."""
    
    def __init__(self, base_dir: str = "/tmp/codebase_docs"):
        """
        Initialize local storage service.
        
        Args:
            base_dir: Base directory for storing documentation
        """
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
    
    def upload_documentation(self, job_id: str, docs_dir: str) -> str:
        """
        Copy generated documentation to local storage.
        
        Args:
            job_id: Unique job identifier
            docs_dir: Local directory containing documentation files
            
        Returns:
            Local file path to the documentation
        """
        try:
            # Create job-specific directory
            job_dir = os.path.join(self.base_dir, job_id)
            
            # Remove if exists (for re-runs)
            if os.path.exists(job_dir):
                shutil.rmtree(job_dir)
            
            # Copy documentation directory
            shutil.copytree(docs_dir, job_dir)
            
            # Return path to main README
            main_readme = os.path.join(job_dir, 'README.md')
            return self.generate_access_url(main_readme)
        
        except Exception as e:
            raise Exception(f"Failed to store documentation locally: {str(e)}")
    
    def generate_access_url(self, file_path: str) -> str:
        """
        Generate a file:// URL for local access.
        
        Args:
            file_path: Path to the file
            
        Returns:
            file:// URL
        """
        # Return backend API URL for serving the file
        # This assumes the backend is running on localhost:8000
        # In a production environment, this should use the configured backend URL
        from config import settings
        base_url = f"http://localhost:{settings.backend_port}"
        # Extract job_id from path (parent directory name)
        job_id = os.path.basename(os.path.dirname(file_path))
        return f"{base_url}/api/docs/{job_id}/README.md"
    
    def upload_json_metadata(self, job_id: str, metadata: dict) -> None:
        """Upload job metadata as JSON to local storage."""
        try:
            job_dir = os.path.join(self.base_dir, job_id)
            os.makedirs(job_dir, exist_ok=True)
            
            metadata_file = os.path.join(job_dir, 'metadata.json')
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to upload metadata: {str(e)}")
    
    def get_documentation_path(self, job_id: str) -> str:
        """Get the local path to documentation for a job."""
        return os.path.join(self.base_dir, job_id)
    
    def list_files(self, job_id: str) -> list:
        """List all files in a job's documentation."""
        job_dir = os.path.join(self.base_dir, job_id)
        if not os.path.exists(job_dir):
            return []
        
        files = []
        for root, dirs, filenames in os.walk(job_dir):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, job_dir)
                files.append(rel_path)
        return files
