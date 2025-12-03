"""FastAPI application for Codebase Documenter."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from celery.result import AsyncResult
import uuid
import os
from config import settings
from celery_app import celery_app
from services.git_service import GitService
from services.local_storage import LocalStorageService


app = FastAPI(
    title="Codebase Documenter API",
    description="AI-powered automatic codebase documentation generator",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class AnalyzeRequest(BaseModel):
    github_url: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "github_url": "https://github.com/username/repository"
            }
        }


class AnalyzeResponse(BaseModel):
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    state: str
    meta: dict = {}
    result: dict = {}


class JobResultResponse(BaseModel):
    job_id: str
    status: str
    s3_url: str = ""
    repo_name: str = ""
    analysis: dict = {}
    error: str = ""


# Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Codebase Documenter API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/api/analyze",
            "status": "/api/status/{job_id}",
            "result": "/api/result/{job_id}",
            "health": "/api/health"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check Redis connection
        celery_app.backend.get("test")
        redis_status = "healthy"
    except:
        redis_status = "unhealthy"
    
    return {
        "status": "healthy",
        "redis": redis_status,
        "environment": settings.environment
    }


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_repository(request: AnalyzeRequest):
    """
    Submit a GitHub repository for analysis and documentation generation.
    
    Args:
        request: AnalyzeRequest with github_url
        
    Returns:
        AnalyzeResponse with job_id and status
    """
    # Validate GitHub URL
    if not GitService.validate_github_url(request.github_url):
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub URL. Please provide a valid GitHub repository URL."
        )
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    try:
        # Submit task to Celery
        task = celery_app.send_task(
            "tasks.analyze_and_document",
            args=[request.github_url, job_id],
            task_id=job_id
        )
        
        return AnalyzeResponse(
            job_id=job_id,
            status="submitted",
            message="Repository analysis started. Use the job_id to check status."
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit job: {str(e)}"
        )


@app.get("/api/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status of a documentation job.
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        JobStatusResponse with current status and metadata
    """
    try:
        task_result = AsyncResult(job_id, app=celery_app)
        
        response = JobStatusResponse(
            job_id=job_id,
            status=task_result.status,
            state=task_result.state,
            meta=task_result.info if isinstance(task_result.info, dict) else {},
            result=task_result.result if task_result.ready() else {}
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job status: {str(e)}"
        )


@app.get("/api/result/{job_id}", response_model=JobResultResponse)
async def get_job_result(job_id: str):
    """
    Get the final result of a completed documentation job.
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        JobResultResponse with S3 URL and metadata
    """
    try:
        task_result = AsyncResult(job_id, app=celery_app)
        
        if not task_result.ready():
            raise HTTPException(
                status_code=202,
                detail="Job is still processing. Please check status endpoint."
            )
        
        if task_result.failed():
            return JobResultResponse(
                job_id=job_id,
                status="failed",
                error=str(task_result.info)
            )
        
        result = task_result.result
        
        return JobResultResponse(
            job_id=job_id,
            status=result.get('status', 'unknown'),
            s3_url=result.get('s3_url', ''),
            repo_name=result.get('repo_name', ''),
            analysis=result.get('analysis', {}),
            error=result.get('error', '')
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job result: {str(e)}"
        )


@app.get("/api/docs/{job_id}/{file_path:path}")
async def serve_documentation(job_id: str, file_path: str = "README.md"):
    """
    Serve documentation files from local storage.
    Only works when STORAGE_MODE=local.
    
    Args:
        job_id: Unique job identifier
        file_path: Path to file within documentation (default: README.md)
        
    Returns:
        File content
    """
    if settings.storage_mode != "local":
        raise HTTPException(
            status_code=400,
            detail="This endpoint only works with local storage mode"
        )
    
    try:
        storage = LocalStorageService()
        doc_path = storage.get_documentation_path(job_id)
        full_path = os.path.join(doc_path, file_path)
        
        # Security check: ensure path is within documentation directory
        if not os.path.abspath(full_path).startswith(os.path.abspath(doc_path)):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(full_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to serve file: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.backend_port)
