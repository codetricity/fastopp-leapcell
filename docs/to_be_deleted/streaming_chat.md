# Streaming Chat Implementation

This document explains the streaming chat functionality implemented in the FastAPI application.

## Overview

The chat system has been enhanced to support **Server-Sent Events (SSE)** for real-time streaming responses from the AI model. This provides a more engaging user experience where responses appear gradually, similar to ChatGPT.

## Architecture

### Components

1. **Backend Streaming Service** (`services/chat_service.py`)
   - `chat_with_llama_stream()`: Streams responses from OpenRouter API
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

## How It Works

### 1. Server-Side Streaming

```python
# routes/chat.py
@router.post("/chat/stream")
async def chat_with_llama_stream(request: Request):
    async def event_generator():
        async for chunk in ChatService.chat_with_llama_stream(user_message):
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

### 2. Client-Side Streaming

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

## Features

### ✅ Real-time Streaming
- Responses appear word-by-word in real-time
- No page refreshes or full response waits
- Smooth user experience

### ✅ Markdown Support
- Server-side markdown processing for each chunk
- Proper HTML rendering of **bold**, *italic*, `code`, etc.
- Code blocks and lists supported

### ✅ Error Handling
- Graceful fallback to mock responses when API unavailable
- Proper error events in SSE stream
- User-friendly error messages

### ✅ Loading States
- Different indicators for "thinking" vs "responding"
- Visual feedback during streaming
- Disabled input during processing

## API Endpoints

### Regular Chat (Non-streaming)
```
POST /api/chat
Content-Type: application/json

{
    "message": "Hello, how are you?"
}
```

### Streaming Chat
```
POST /api/chat/stream
Content-Type: application/json

{
    "message": "Hello, how are you?"
}
```

**Response:** Server-Sent Events stream with:
- `event: message` - Content chunks
- `event: complete` - Stream completion
- `event: error` - Error messages

## Testing

### Manual Testing
1. Visit `http://localhost:8000/ai-demo`
2. Type a message and press Enter
3. Watch the response stream in real-time

### Automated Testing
```bash
# Run the test script
uv run python test_streaming.py
```

## Dependencies

- **sse-starlette**: Server-Sent Events implementation
- **aiohttp**: Async HTTP client for API calls
- **markdown**: Markdown-to-HTML conversion
- **Fetch API**: Client-side streaming (native browser support)
- **Alpine.js**: Reactive UI updates

## Configuration

### Environment Variables
```bash
OPENROUTER_API_KEY=your_api_key_here
```

### Fallback Behavior
When the OpenRouter API is unavailable (rate limits, network issues, etc.), the system automatically falls back to mock responses for testing purposes.

## Performance Considerations

- **Chunked Responses**: Each chunk is processed individually
- **Markdown Processing**: Applied per chunk for immediate rendering
- **Memory Efficiency**: No large response buffering
- **Connection Management**: Proper SSE connection handling

## Future Enhancements

- [ ] Add typing indicators
- [ ] Support for conversation history
- [ ] Multiple AI model selection
- [ ] Response streaming controls (pause/resume)
- [ ] Export conversation functionality 