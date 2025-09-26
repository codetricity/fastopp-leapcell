"""
Webinar service for handling webinar registrant business logic
"""
import os
from pathlib import Path
from typing import Optional
from uuid import UUID
import uuid
from sqlmodel import select
from db import SessionLocal
from models import WebinarRegistrants


class WebinarService:
    """Service for webinar registrant operations"""
    
    @staticmethod
    def get_all_registrants():
        """Get all webinar registrants with their photos"""
        with SessionLocal() as session:
            result = session.execute(select(WebinarRegistrants))
            registrants = result.scalars().all()
            
            return [
                {
                    "id": str(registrant.id),
                    "name": registrant.name,
                    "email": registrant.email,
                    "company": registrant.company,
                    "webinar_title": registrant.webinar_title,
                    "webinar_date": registrant.webinar_date.isoformat(),
                    "status": registrant.status,
                    "photo_url": registrant.photo_url,
                    "notes": registrant.notes,
                    "registration_date": registrant.registration_date.isoformat()
                }
                for registrant in registrants
            ]
    
    @staticmethod
    def get_webinar_attendees():
        """Get webinar attendees for the marketing demo page"""
        with SessionLocal() as session:
            result = session.execute(select(WebinarRegistrants))
            registrants = result.scalars().all()
            
            return [
                {
                    "id": str(registrant.id),
                    "name": registrant.name,
                    "email": registrant.email,
                    "company": registrant.company,
                    "webinar_title": registrant.webinar_title,
                    "webinar_date": registrant.webinar_date.isoformat(),
                    "status": registrant.status,
                    "group": registrant.group,
                    "notes": registrant.notes,
                    "photo_url": registrant.photo_url,
                    "created_at": registrant.created_at.isoformat()
                }
                for registrant in registrants
            ]
    
    @staticmethod
    def upload_photo(registrant_id: str, photo_content: bytes, filename: str) -> tuple[bool, str, Optional[str]]:
        """
        Upload a photo for a webinar registrant
        
        Environment-based storage:
        - development: Local file storage (/static/uploads)
        - production: Object storage (S3/CDN)
        
        Returns:
            tuple: (success, message, photo_url)
        """
        try:
            from dependencies.config import get_settings
            from pathlib import Path
            
            settings = get_settings()
            
            # Check environment to determine storage method
            if settings.environment == "development":
                return WebinarService._upload_photo_local(registrant_id, photo_content, filename, settings)
            else:
                return WebinarService._upload_photo_s3(registrant_id, photo_content, filename, settings)
                
        except Exception as e:
            return False, f"Failed to upload photo: {str(e)}", None
    
    @staticmethod
    def _upload_photo_local(registrant_id: str, photo_content: bytes, filename: str, settings) -> tuple[bool, str, Optional[str]]:
        """Upload photo to local file system (development)"""
        try:
            from uuid import UUID
            from sqlmodel import select
            
            # Generate unique filename
            file_extension = Path(filename).suffix if filename else '.jpg'
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Save to local file system
            upload_dir = Path(settings.upload_dir)
            photos_dir = upload_dir / "photos"
            photos_dir.mkdir(parents=True, exist_ok=True)
            
            local_path = photos_dir / unique_filename
            with open(local_path, "wb") as f:
                f.write(photo_content)
            
            # Generate local URL
            photo_url = f"/static/uploads/photos/{unique_filename}"
            
            # Update database
            try:
                registrant_uuid = UUID(registrant_id)
            except ValueError:
                return False, "Invalid registrant ID", None
            
            with SessionLocal() as session:
                result = session.execute(
                    select(WebinarRegistrants).where(WebinarRegistrants.id == registrant_uuid)
                )
                registrant = result.scalar_one_or_none()
                
                if not registrant:
                    return False, "Registrant not found", None
                
                registrant.photo_url = photo_url
                session.commit()
            
            return True, "Photo uploaded successfully to local storage!", photo_url
            
        except Exception as e:
            return False, f"Local upload failed: {str(e)}", None
    
    @staticmethod
    def _upload_photo_s3(registrant_id: str, photo_content: bytes, filename: str, settings) -> tuple[bool, str, Optional[str]]:
        """Upload photo to object storage (production)"""
        try:
            import boto3
            from botocore.exceptions import ClientError
            from uuid import UUID
            from sqlmodel import select
            
            # Check S3 credentials
            s3_access_key = os.getenv("S3_ACCESS_KEY")
            s3_secret_key = os.getenv("S3_SECRET_KEY")
            s3_bucket = os.getenv("S3_BUCKET")
            s3_endpoint_url = os.getenv("S3_ENDPOINT_URL", "https://objstorage.leapcell.io")
            s3_region = os.getenv("S3_REGION", "us-east-1")
            
            if not all([s3_access_key, s3_secret_key, s3_bucket]):
                return False, "S3 credentials not configured", None
            
            # Generate unique filename
            file_extension = Path(filename).suffix if filename else '.jpg'
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Initialize S3 client
            s3_client = boto3.client(
                's3',
                aws_access_key_id=s3_access_key,
                aws_secret_access_key=s3_secret_key,
                endpoint_url=s3_endpoint_url,
                region_name=s3_region
            )
            
            # Upload to Object Storage
            s3_key = f"photos/{unique_filename}"
            s3_client.put_object(
                Bucket=s3_bucket,
                Key=s3_key,
                Body=photo_content,
                ContentType='image/jpeg'
            )
            
            # Generate CDN URL using the user's S3 bucket
            # For LeapCell, the CDN URL format is: https://{account_id}.leapcellobj.com/{bucket}/{key}
            # Try to get CDN URL from environment variable, otherwise construct it
            cdn_base_url = os.getenv("S3_CDN_URL")
            if cdn_base_url:
                # CDN base URL already includes the bucket, just append the key
                photo_url = f"{cdn_base_url}/{s3_key}"
            else:
                # Fallback: use the S3 endpoint URL (may not work for CDN)
                photo_url = f"{s3_endpoint_url}/{s3_bucket}/{s3_key}"
            
            # Convert string to UUID
            try:
                registrant_uuid = UUID(registrant_id)
            except ValueError:
                return False, "Invalid registrant ID", None
            
            with SessionLocal() as session:
                result = session.execute(
                    select(WebinarRegistrants).where(WebinarRegistrants.id == registrant_uuid)
                )
                registrant = result.scalar_one_or_none()
                
                if not registrant:
                    return False, "Registrant not found", None
                
                registrant.photo_url = photo_url
                session.commit()
            
            return True, "Photo uploaded successfully to Object Storage!", photo_url
            
        except ClientError as e:
            return False, f"S3 upload failed: {str(e)}", None
        except Exception as e:
            return False, f"Failed to upload photo: {str(e)}", None
    
    @staticmethod
    def update_notes(registrant_id: str, notes: str) -> tuple[bool, str]:
        """
        Update notes for a webinar registrant
        
        Returns:
            tuple: (success, message)
        """
        try:
            # Convert string to UUID
            try:
                registrant_uuid = UUID(registrant_id)
            except ValueError:
                return False, "Invalid registrant ID"
            
            with SessionLocal() as session:
                result = session.execute(
                    select(WebinarRegistrants).where(WebinarRegistrants.id == registrant_uuid)
                )
                registrant = result.scalar_one_or_none()
                
                if not registrant:
                    return False, "Registrant not found"
                
                # Update database
                registrant.notes = notes
                session.commit()
            
            return True, "Notes updated successfully!"
            
        except Exception as e:
            return False, f"Error updating notes: {str(e)}"
    
    @staticmethod
    def delete_photo(registrant_id: str) -> tuple[bool, str]:
        """
        Delete a photo for a webinar registrant
        
        Returns:
            tuple: (success, message)
        """
        try:
            # Convert string to UUID
            try:
                registrant_uuid = UUID(registrant_id)
            except ValueError:
                return False, "Invalid registrant ID"
            
            with SessionLocal() as session:
                result = session.execute(
                    select(WebinarRegistrants).where(WebinarRegistrants.id == registrant_uuid)
                )
                registrant = result.scalar_one_or_none()
                
                if not registrant:
                    return False, "Registrant not found"
                
                if not registrant.photo_url:
                    return False, "No photo found for this registrant"
                
                # Delete file from filesystem
                photo_path = Path("static") / registrant.photo_url.lstrip("/static/")
                try:
                    if photo_path.exists():
                        photo_path.unlink()
                except Exception as e:
                    # Log error but don't fail the request
                    print(f"Failed to delete file {photo_path}: {e}")
                
                # Update database
                registrant.photo_url = None
                session.commit()
            
            return True, "Photo deleted successfully!"
            
        except Exception as e:
            return False, f"Error deleting photo: {str(e)}" 