"""Storage service for Cloudflare R2 interaction."""
from __future__ import annotations

import boto3
from botocore.config import Config
from app.core.config import settings

class StorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.r2_endpoint_url,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4"),
            region_name=settings.R2_REGION,
        )
        self.bucket = settings.R2_BUCKET_NAME

    def generate_upload_url(self, file_key: str, expires_in: int = 900) -> str:
        """Generate a pre-signed URL for uploading a file."""
        return self.s3_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self.bucket, "Key": file_key},
            ExpiresIn=expires_in,
        )

    def generate_download_url(self, file_key: str, expires_in: int = 900) -> str:
        """Generate a pre-signed URL for downloading a file."""
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": file_key},
            ExpiresIn=expires_in,
        )

    def delete_file(self, file_key: str):
        """Delete a file from the bucket."""
        self.s3_client.delete_object(Bucket=self.bucket, Key=file_key)
