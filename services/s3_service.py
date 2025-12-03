import os
import json
import boto3
from botocore.exceptions import ClientError
from config import settings


class S3Service:
    """Service for handling AWS S3 operations."""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        self.bucket_name = settings.s3_bucket_name
    
    def upload_documentation(self, job_id: str, docs_dir: str) -> str:
        """
        Upload generated documentation to S3.
        
        Args:
            job_id: Unique job identifier
            docs_dir: Local directory containing documentation files
            
        Returns:
            S3 URL of the uploaded documentation
        """
        try:
            # Upload all files in the documentation directory
            for root, dirs, files in os.walk(docs_dir):
                for file in files:
                    local_path = os.path.join(root, file)
                    # Create S3 key with job_id prefix
                    relative_path = os.path.relpath(local_path, docs_dir)
                    s3_key = f"{job_id}/{relative_path}"
                    
                    # Determine content type
                    content_type = self._get_content_type(file)
                    
                    # Upload file
                    self.s3_client.upload_file(
                        local_path,
                        self.bucket_name,
                        s3_key,
                        ExtraArgs={'ContentType': content_type}
                    )
            
            # Generate presigned URL for the main README
            main_readme_key = f"{job_id}/README.md"
            url = self.generate_presigned_url(main_readme_key)
            
            return url
        except ClientError as e:
            raise Exception(f"Failed to upload documentation to S3: {str(e)}")
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 86400) -> str:
        """
        Generate a presigned URL for accessing S3 object.
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default: 24 hours)
            
        Returns:
            Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
    
    def upload_json_metadata(self, job_id: str, metadata: dict) -> None:
        """Upload job metadata as JSON to S3."""
        try:
            s3_key = f"{job_id}/metadata.json"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json.dumps(metadata, indent=2),
                ContentType='application/json'
            )
        except ClientError as e:
            raise Exception(f"Failed to upload metadata: {str(e)}")
    
    @staticmethod
    def _get_content_type(filename: str) -> str:
        """Determine content type based on file extension."""
        extension = os.path.splitext(filename)[1].lower()
        content_types = {
            '.md': 'text/markdown',
            '.html': 'text/html',
            '.json': 'application/json',
            '.txt': 'text/plain',
            '.css': 'text/css',
            '.js': 'application/javascript',
        }
        return content_types.get(extension, 'application/octet-stream')
