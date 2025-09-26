#!/usr/bin/env python3
"""
Script to restore sample photos to Object Storage for production
"""

import asyncio
import boto3
import os
from pathlib import Path

async def restore_sample_photos_to_s3():
    """Restore sample photos from local static/uploads/sample_photos to Object Storage"""
    
    # Check S3 credentials
    s3_access_key = os.getenv("S3_ACCESS_KEY")
    s3_secret_key = os.getenv("S3_SECRET_KEY")
    s3_bucket = os.getenv("S3_BUCKET")
    
    if not s3_access_key or not s3_secret_key:
        print("❌ S3 credentials not configured. Set S3_ACCESS_KEY and S3_SECRET_KEY environment variables.")
        return
    
    if not s3_bucket:
        print("❌ S3 bucket not configured. Set S3_BUCKET environment variable.")
        return
    
    # Initialize S3 client
    s3 = boto3.client(
        "s3",
        region_name=os.getenv("S3_REGION", "us-east-1"),
        endpoint_url=os.getenv("S3_ENDPOINT_URL", "https://objstorage.leapcell.io"),
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key
    )
    
    # Find sample photos
    sample_photos_dir = Path("static/uploads/sample_photos")
    if not sample_photos_dir.exists():
        print(f"❌ Sample photos directory not found: {sample_photos_dir}")
        return
    
    print(f"📸 Found sample photos directory: {sample_photos_dir}")
    
    # Upload each sample photo
    uploaded_count = 0
    for photo_file in sample_photos_dir.glob("*.jpg"):
        try:
            # Create S3 key
            s3_key = f"uploads/photos/{photo_file.name}"
            
            # Upload to S3
            with open(photo_file, "rb") as f:
                s3.put_object(
                    Bucket=s3_bucket,
                    Key=s3_key,
                    Body=f,
                    ContentType="image/jpeg"
                )
            
            print(f"✅ Uploaded {photo_file.name} to {s3_key}")
            uploaded_count += 1
            
        except Exception as e:
            print(f"❌ Failed to upload {photo_file.name}: {e}")
    
    print(f"\n🎉 Successfully uploaded {uploaded_count} sample photos to Object Storage")
    print("💡 These photos will now be available via the /static/uploads/photos/ endpoint")

if __name__ == "__main__":
    asyncio.run(restore_sample_photos_to_s3())
