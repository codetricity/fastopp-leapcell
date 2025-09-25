# Application Features

This document covers the core features of the FastOpp application, including file management, AI chat system, webinar management, and admin interface functionality.

## File Management

### Overview

The application supports uploading photos for webinar registrants. Photos are stored in the `static/uploads/photos/` directory and referenced in the database via the `photo_url` field.

### Database Schema

The `WebinarRegistrants` model has been updated to include a `photo_url` field:

```python
class WebinarRegistrants(SQLModel, table=True):
    # ... existing fields ...
    photo_url: Optional[str] = Field(default=None, nullable=True)  # Path to uploaded photo
```

### API Endpoints

#### Upload Photo
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

#### Get All Registrants
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

#### Delete Photo
- **DELETE** `/delete-photo/{registrant_id}`
- **Response:**
  ```json
  {
    "success": true,
    "message": "Photo deleted successfully"
  }
  ```

### Web Interface

Visit `/webinar-registrants` to access the web interface for managing webinar registrants and their photos.

**Features:**
- Upload photos for specific registrants
- View all registrants with their photos
- Delete photos
- Real-time updates

### File Storage

- **Directory:** `static/uploads/photos/`
- **File naming:** UUID-based to prevent conflicts
- **Supported formats:** All image types (JPEG, PNG, GIF, etc.)
- **Size limit:** 5MB per file
- **Validation:** Only image files are accepted

## Image Storage Structure

### Directory Structure

```
static/
├── uploads/
│   ├── photos/           # User-uploaded photos (UUID-based filenames)
│   └── sample_photos/    # Pre-loaded fake people images
└── images/               # Other static images (logos, etc.)
```

### Sample Photos

The application includes 5 sample professional headshots from Unsplash:

- `john_smith.jpg` - John Smith (Tech Corp)
- `sarah_johnson.jpg` - Sarah Johnson (Startup Inc)
- `michael_chen.jpg` - Michael Chen (Enterprise Solutions)
- `emily_davis.jpg` - Emily Davis (Freelance Developer)
- `david_wilson.jpg` - David Wilson (Tech Consulting)

### Setup Instructions

#### 1. Download Sample Photos
```bash
uv run python -m scripts.download_sample_photos
```

#### 2. Add Registrants with Photos
```bash
uv run python -m scripts.clear_and_add_registrants
```

### How It Works

#### **Sample Photos Storage**
- **Location**: `static/uploads/sample_photos/`
- **Purpose**: Source images for initialization
- **Format**: High-quality professional headshots
- **License**: Free to use (Unsplash)

#### **User Photos Storage**
- **Location**: `static/uploads/photos/`
- **Naming**: UUID-based unique filenames
- **Purpose**: Actual user-uploaded photos
- **Security**: Prevents filename conflicts

#### **Database Integration**
- **Field**: `photo_url` in `WebinarRegistrants` table
- **Format**: Relative path (e.g., `/static/uploads/photos/uuid_filename.jpg`)
- **Validation**: Only image files accepted
- **Size Limit**: 5MB per file

### Available Scripts

#### **Download Sample Photos**
```bash
uv run python -m scripts.download_sample_photos
```
- Downloads professional headshots from Unsplash
- Saves to `static/uploads/sample_photos/`
- Handles errors gracefully

#### **Add Registrants with Photos**
```bash
uv run python -m scripts.add_sample_webinar_registrants
```
- Adds registrants without clearing existing ones
- Copies sample photos to user photos directory
- Generates unique filenames

#### **Clear and Add Registrants**
```bash
uv run python -m scripts.clear_and_add_registrants
```
- Clears all existing registrants
- Adds fresh registrants with photos
- Perfect for demo resets

### Usage Examples

#### **For Development**
1. Run download script to get sample photos
2. Run clear_and_add script for fresh demo data
3. Access `/webinar-registrants` to see photos

#### **For Production**
1. Replace sample photos with your own images
2. Update the initialization script with new filenames
3. Deploy with your custom images

#### **Adding New Sample Photos**
1. Add new images to `static/uploads/sample_photos/`
2. Update the registrants list in the script
3. Run the initialization script

### Security Considerations

- **File Type Validation**: Only image files are accepted
- **Size Limits**: 5MB maximum file size
- **Unique Naming**: UUID-based filenames prevent conflicts
- **Path Validation**: Relative paths only, no directory traversal
- **Access Control**: Photos are publicly accessible (consider authentication for sensitive images)

## AI Chat System

### Overview

The chat system has been enhanced to support **Server-Sent Events (SSE)** for real-time streaming responses from the AI model. This provides a more engaging user experience where responses appear gradually, similar to ChatGPT.

### Architecture

#### Components

1. **Backend Streaming Service** (`services/chat_service.py`)
   - `chat_with_llma_stream()`: Streams responses from OpenRouter API
   - `_mock_stream_response()`: Fallback mock responses for testing
   - Handles markdown-to-HTML conversion for each chunk

2. **Streaming Route** (`routes/chat.py`)
   - `/api/chat/stream`: SSE endpoint for streaming responses
   - Uses `sse-starlette` for proper SSE implementation
   - Returns `EventSourceResponse` with proper headers

3. **Frontend Integration** (`templates/ai-demo.html`)
   - HTMX SSE for client-side streaming
   - Alpine.js for reactive UI updates
   - Real-time message appending

### How It Works

#### 1. Server-Side Streaming

```python
# routes/chat.py
@router.post("/chat/stream")
async def chat_with_llma_stream(request: Request):
    async def event_generator():
        async for chunk in ChatService.chat_with_llma_stream(user_message):
            yield {
                "event": "message",
                "data": json.dumps(chunk)
            }
        yield {
            "event": "complete",
            "data": json.dumps({"status": "completed"})
        }
    
    return EventSourceResponse(event_generator())
```

#### 2. Client-Side Streaming

```javascript
// templates/ai-demo.html
fetch('/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: userMessage })
})
.then(response => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    function readStream() {
        return reader.read().then(({ done, value }) => {
            if (done) {
                this.isLoading = false;
                this.currentStreamingMessage = null;
                return;
            }
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));
                    if (data.content) {
                        this.currentStreamingMessage.content += data.content;
                    }
                }
            }
            
            return readStream();
        });
    }
    
    return readStream();
});
```

### Features

#### ✅ Real-time Streaming
- Responses appear word-by-word in real-time
- No page refreshes or full response waits
- Smooth user experience

#### ✅ Markdown Support
- Server-side markdown processing for each chunk
- Proper HTML rendering of **bold**, *italic*, `code`, etc.

#### ✅ Error Handling
- Graceful fallback to mock responses
- Connection error handling
- Timeout management

#### ✅ Multiple AI Models
- OpenRouter API integration
- Support for GPT-4, Claude, Llama, and others
- Easy model switching

### Configuration

#### Environment Variables

```bash
# OpenRouter API configuration
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=gpt-4
```

#### Model Selection

```python
# Available models
MODELS = {
    "gpt-4": "openai/gpt-4",
    "claude": "anthropic/claude-3-opus",
    "llama": "meta-llama/llama-3.1-8b-instruct",
    "gemini": "google/gemini-pro"
}
```

## Webinar Management

### Overview

The webinar management system allows users to:

- Create and manage webinars
- Register attendees
- Track registration status
- Manage attendee photos and information
- Filter and search registrants

### Features

#### **Webinar Creation**
- Title and description
- Date and time scheduling
- Capacity limits
- Registration requirements

#### **Attendee Management**
- Registration forms
- Photo uploads
- Status tracking (registered, attended, cancelled)
- Notes and comments

#### **Permission-Based Access**
- Marketing users: Full webinar management
- Sales users: View assigned registrants only
- Support users: Limited access
- Superusers: Complete access

### API Endpoints

#### Webinar Management
- `GET /api/webinars` - List all webinars
- `POST /api/webinars` - Create new webinar
- `PUT /api/webinars/{id}` - Update webinar
- `DELETE /api/webinars/{id}` - Delete webinar

#### Registration Management
- `GET /api/webinar-attendees` - List attendees
- `POST /api/register` - Register for webinar
- `PUT /api/registrants/{id}` - Update registration
- `DELETE /api/registrants/{id}` - Cancel registration

## Admin Interface

### Overview

The admin interface provides a comprehensive management system for:

- User management and permissions
- Product catalog management
- Webinar and registration oversight
- System configuration

### Features

#### **User Management**
- Create, edit, and delete users
- Assign user groups and permissions
- Manage user status (active/inactive)
- Password reset functionality

#### **Product Management**
- Product catalog CRUD operations
- Category management
- Inventory tracking
- Pricing management

#### **Webinar Oversight**
- View all registrations
- Export registration data
- Manage attendee information
- Track attendance statistics

#### **System Administration**
- Database management
- Migration control
- Backup and restore
- System monitoring

### Permission System

The admin interface implements a sophisticated permission system:

- **Group-based access control**
- **Model-specific permissions**
- **Action-based permissions (CRUD)**
- **Data filtering by user role**
- **Audit trail logging**

## Usage Examples

### File Upload with curl

```bash
curl -X POST "http://localhost:8000/upload-photo/2dc430ba941e489a9c3bdaaccef034ea" \
  -F "photo=@/path/to/photo.jpg" \
  -F "description=Professional headshot"
```

### Python API Client

```python
import requests

# Upload photo
with open('photo.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload-photo/uuid',
        files={'photo': f},
        data={'description': 'Professional headshot'}
    )

# Get registrants
response = requests.get('http://localhost:8000/registrants')
registrants = response.json()['registrants']
```

### AI Chat Integration

```python
# Stream chat response
async def chat_with_ai(message: str):
    async with httpx.AsyncClient() as client:
        async with client.stream(
            'POST',
            'http://localhost:8000/api/chat/stream',
            json={'message': message}
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    yield data
```

## Next Steps

After exploring the features:

1. **Test File Uploads**: Try uploading photos for webinar registrants
2. **Experiment with AI Chat**: Test the streaming chat functionality
3. **Manage Webinars**: Create and manage webinar registrations
4. **Customize Admin Panel**: Adapt the interface for your needs

For more information, see:
- [POSTGRESQL_SETUP.md](deployment/POSTGRESQL_SETUP.md) - PostgreSQL setup and database configuration
- [DATABASE.md](DATABASE.md) - Database management and migrations
- [AUTHENTICATION.md](AUTHENTICATION.md) - User authentication and permissions
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture overview
