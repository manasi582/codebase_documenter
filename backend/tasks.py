"""Celery tasks for asynchronous processing."""
import os
import shutil
from celery import Task
from celery_app import celery_app
from config import settings
from services.git_service import GitService
from services.s3_service import S3Service
from services.local_storage import LocalStorageService
from services.file_analyzer import FileAnalyzer
from ai_agent.agent import DocumentationAgent


class CallbackTask(Task):
    """Base task with callbacks."""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        print(f"Task {task_id} failed: {exc}")
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success."""
        print(f"Task {task_id} completed successfully")


@celery_app.task(base=CallbackTask, bind=True, name="tasks.analyze_and_document")
def analyze_and_document(self, github_url: str, job_id: str) -> dict:
    """
    Main task to analyze repository and generate documentation.
    
    Args:
        github_url: GitHub repository URL
        job_id: Unique job identifier
        
    Returns:
        Dictionary with status and results
    """
    repo_path = None
    docs_dir = None
    
    try:
        # Update task state
        self.update_state(state='CLONING', meta={'status': 'Cloning repository...'})
        
        # Clone repository
        git_service = GitService()
        repo_path, repo_name = git_service.clone_repository(github_url)
        
        # Update task state
        self.update_state(state='ANALYZING', meta={'status': 'Analyzing codebase...'})
        
        # Run AI agent
        agent = DocumentationAgent()
        result = agent.run(repo_path, repo_name)
        
        if result.get('error'):
            raise Exception(result['error'])
        
        # Update task state
        self.update_state(state='GENERATING', meta={'status': 'Generating documentation...'})
        
        # Create documentation directory
        docs_dir = f"/tmp/docs_{job_id}"
        os.makedirs(docs_dir, exist_ok=True)
        
        # Write main README
        with open(os.path.join(docs_dir, 'README.md'), 'w') as f:
            f.write(result['main_readme'])
        
        # Write folder READMEs
        for folder, content in result['folder_readmes'].items():
            folder_path = os.path.join(docs_dir, folder)
            os.makedirs(folder_path, exist_ok=True)
            with open(os.path.join(folder_path, 'README.md'), 'w') as f:
                f.write(content)
        
        # Write function documentation
        if result['function_docs']:
            func_docs_dir = os.path.join(docs_dir, 'detailed_docs')
            os.makedirs(func_docs_dir, exist_ok=True)
            for file_path, content in result['function_docs'].items():
                # Create safe filename
                safe_name = file_path.replace('/', '_').replace('.', '_') + '.md'
                with open(os.path.join(func_docs_dir, safe_name), 'w') as f:
                    f.write(f"# {file_path}\n\n{content}")
        
        # Write setup guide
        with open(os.path.join(docs_dir, 'SETUP.md'), 'w') as f:
            f.write(result['setup_guide'])
        
        # Update task state
        storage_type = "local storage" if settings.storage_mode == "local" else "S3"
        self.update_state(state='UPLOADING', meta={'status': f'Saving to {storage_type}...'})
        
        # Upload based on storage mode
        if settings.storage_mode == "s3":
            storage_service = S3Service()
            doc_url = storage_service.upload_documentation(job_id, docs_dir)
        else:
            storage_service = LocalStorageService()
            doc_url = storage_service.upload_documentation(job_id, docs_dir)
        
        # Upload metadata
        metadata = {
            'job_id': job_id,
            'github_url': github_url,
            'repo_name': repo_name,
            'analysis': {
                'total_files': result['analysis']['total_files'],
                'code_files': result['analysis']['code_file_count'],
                'languages': result['analysis']['languages'],
                'frameworks': result['analysis']['frameworks']
            },
            'status': 'completed'
        }
        storage_service.upload_json_metadata(job_id, metadata)
        
        return {
            'status': 'completed',
            'job_id': job_id,
            's3_url': doc_url,  # Keep key name for backward compatibility
            'repo_name': repo_name,
            'analysis': metadata['analysis']
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'job_id': job_id,
            'error': str(e)
        }
    
    finally:
        # Cleanup
        if repo_path:
            GitService.cleanup_repository(repo_path)
        if docs_dir and os.path.exists(docs_dir):
            shutil.rmtree(docs_dir)
