# File Upload for Webinar Attendees

This document explains how to implement and use the file upload functionality for webinar attendees in the FastAPI application.

## Overview

The application now supports uploading photos for webinar registrants. Photos are stored in the `static/uploads/photos/` directory and referenced in the database via the `photo_url` field.

## Database Schema

The `WebinarRegistrants` model has been updated to include a `photo_url` field:

```python
class WebinarRegistrants(SQLModel, table=True):
    # ... existing fields ...
    photo_url: Optional[str] = Field(default=None, nullable=True)  # Path to uploaded photo
```

## API Endpoints

### Upload Photo
- **POST** `/upload-photo/{registrant_id}`
- **Parameters:**
  - `registrant_id`: UUID of the webinar registrant
  - `photo`: Image file (multipart/form-data)
  - `description`: Optional description (form field)
- **Response:**
  ```json
  {
    "success": true,
    "photo_url": "/static/uploads/photos/uuid.jpg",
    "message": "Photo uploaded successfully"
  }
  ```

### Get All Registrants
- **GET** `/registrants`
- **Response:**
  ```json
  {
    "registrants": [
      {
        "id": "uuid",
        "name": "John Smith",
        "email": "john@example.com",
        "company": "Tech Corp",
        "webinar_title": "Advanced FastAPI Development",
        "webinar_date": "2024-02-15T14:00:00",
        "status": "registered",
        "photo_url": "/static/uploads/photos/uuid.jpg",
        "registration_date": "2024-02-15T14:00:00"
      }
    ]
  }
  ```

### Delete Photo
- **DELETE** `/delete-photo/{registrant_id}`
- **Response:**
  ```json
  {
    "success": true,
    "message": "Photo deleted successfully"
  }
  ```

## Web Interface

Visit `/webinar-registrants` to access the web interface for managing webinar registrants and their photos.

### Features:
- Upload photos for specific registrants
- View all registrants with their photos
- Delete photos
- Real-time updates

## File Storage

- **Directory:** `static/uploads/photos/`
- **File naming:** UUID-based to prevent conflicts
- **Supported formats:** All image types (JPEG, PNG, GIF, etc.)
- **Size limit:** 5MB per file
- **Validation:** Only image files are accepted

## Usage Examples

### Using curl to upload a photo:

```bash
curl -X POST "http://localhost:8000/upload-photo/2dc430ba941e489a9c3bdaaccef034ea" \
  -F "photo=@/path/to/photo.jpg" \
  -F "description=Professional headshot"
```

### Using Python requests:

```python
import requests

# Upload photo
with open('photo.jpg', 'rb') as f:
    files = {'photo': f}
    data = {'description': 'Professional headshot'}
    response = requests.post(
        'http://localhost:8000/upload-photo/2dc430ba941e489a9c3bdaaccef034ea',
        files=files,
        data=data
    )
    print(response.json())

# Get all registrants
response = requests.get('http://localhost:8000/registrants')
registrants = response.json()
print(registrants)

# Delete photo
response = requests.delete('http://localhost:8000/delete-photo/2dc430ba941e489a9c3bdaaccef034ea')
print(response.json())
```

## Security Considerations

1. **File type validation:** Only image files are accepted
2. **File size limits:** 5MB maximum per file
3. **Unique filenames:** UUID-based naming prevents conflicts
4. **Path traversal protection:** Files are stored in a controlled directory
5. **Database validation:** Registrant existence is verified before upload

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- **400 Bad Request:** Invalid file type or size
- **404 Not Found:** Registrant not found
- **500 Internal Server Error:** File system errors

## Testing

1. Start the application: `uv run uvicorn main:app --reload`
2. Visit `http://localhost:8000/webinar-registrants`
3. Use the web interface to upload and manage photos
4. Test the API endpoints directly using curl or a tool like Postman

## Sample Data

Run the sample data script to add test registrants:

```bash
uv run python -m scripts.add_sample_webinar_registrants
```

This will add 5 sample webinar registrants that you can use for testing the photo upload functionality. 