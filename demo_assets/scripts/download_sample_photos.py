#!/usr/bin/env python3
"""
Script to download sample fake people images for the webinar registrants demo
"""

import requests
from pathlib import Path

# Sample photos from Unsplash (free to use)
SAMPLE_PHOTOS = [
    {
        "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face",
        "filename": "john_smith.jpg",
        "description": "Professional headshot of John Smith"
    },
    {
        "url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&h=200&fit=crop&crop=face",
        "filename": "sarah_johnson.jpg",
        "description": "Professional headshot of Sarah Johnson"
    },
    {
        "url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop&crop=face",
        "filename": "michael_chen.jpg",
        "description": "Professional headshot of Michael Chen"
    },
    {
        "url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&h=200&fit=crop&crop=face",
        "filename": "emily_davis.jpg",
        "description": "Professional headshot of Emily Davis"
    },
    {
        "url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&h=200&fit=crop&crop=face",
        "filename": "david_wilson.jpg",
        "description": "Professional headshot of David Wilson"
    }
]


def download_sample_photos():
    """Download sample photos for the demo"""
    sample_dir = Path("static/uploads/sample_photos")
    sample_dir.mkdir(exist_ok=True)
    
    print("Downloading sample photos...")
    
    for photo in SAMPLE_PHOTOS:
        filename = sample_dir / photo["filename"]
        
        if filename.exists():
            print(f"✓ {photo['filename']} already exists")
            continue
            
        try:
            response = requests.get(photo["url"], timeout=10)
            response.raise_for_status()
            
            with open(filename, "wb") as f:
                f.write(response.content)
            
            print(f"✓ Downloaded {photo['filename']}")
            
        except Exception as e:
            print(f"✗ Failed to download {photo['filename']}: {e}")
    
    print(f"\nSample photos downloaded to: {sample_dir}")
    print("You can now use these in your initialization script!")


if __name__ == "__main__":
    download_sample_photos() 