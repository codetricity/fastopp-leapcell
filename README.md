# FastOpp - PostgreSQL Edition for LeapCell Deployment

![FastOpp Logo](docs/images/fastopp_logo.webp)

## What

**Special PostgreSQL-optimized version of FastOpp** designed for deployment on LeapCell and other PostgreSQL-based platforms. This version uses **synchronous database communication** for improved reliability and compatibility with managed PostgreSQL services.

This is a modified version of the original [FastOpp](https://github.com/Oppkey/FastOpp) project, specifically optimized for:
- **PostgreSQL databases** (instead of SQLite)
- **Synchronous database operations** (instead of async)
- **LeapCell platform deployment** (tested and verified)
- **Production-ready database connections** with proper SSL and timeout handling

## Key Differences from Original FastOpp

### Database Architecture Changes
- **Original FastOpp**: SQLite with async database operations (`AsyncSession`)
- **This Version**: PostgreSQL with synchronous database operations (`Session`)
- **Driver**: Uses `psycopg2-binary` instead of `asyncpg` for better LeapCell compatibility
- **Connection Management**: Optimized for managed PostgreSQL services with SSL and timeout handling

### Async vs Sync Database Operations

This version represents a significant architectural change from async to synchronous database operations. Here's a detailed analysis:

#### **Why We Switched to Sync**

**1. Serverless Platform Compatibility**
- **LeapCell Requirements**: LeapCell's managed PostgreSQL works better with synchronous connections
- **Connection Pooling**: Synchronous connections are more predictable in serverless environments
- **Timeout Issues**: Async connections can timeout unexpectedly in serverless contexts
- **SSL Configuration**: Synchronous drivers handle SSL certificates more reliably

**2. Simplified Debugging and Maintenance**
- **Easier Error Handling**: Synchronous code is easier to debug and trace
- **Reduced Complexity**: No need to manage async context managers throughout the codebase
- **Better Stack Traces**: Synchronous errors provide clearer debugging information
- **Easier Testing**: Unit tests are simpler without async/await complexity

**3. Production Reliability**
- **Connection Stability**: Synchronous connections are more stable for managed databases
- **Fewer Race Conditions**: Eliminates async-related concurrency issues
- **Predictable Performance**: More consistent response times
- **Better Error Recovery**: Easier to implement retry logic and error handling

#### **Trade-offs: What We Gained vs Lost**

**✅ What We Gained:**
- **Better Reliability**: Fewer connection timeout issues with managed PostgreSQL
- **Simplified Codebase**: Easier to understand and maintain
- **Serverless Compatibility**: Works better with LeapCell and similar platforms
- **Easier Debugging**: Clearer error messages and stack traces
- **Production Stability**: More predictable behavior in production environments
- **Reduced Dependencies**: Fewer async-related packages and complexity

**❌ What We Lost:**
- **Concurrency Benefits**: Cannot handle multiple database operations concurrently
- **Async Ecosystem**: Cannot use async database drivers like `asyncpg`
- **Performance Scaling**: Limited by single-threaded database operations
- **Modern Async Patterns**: Cannot leverage async/await for database operations

#### **When Sync is Better vs When Async is Better**

**Synchronous is Better For:**
- **Demo/Educational Applications**: Simpler to understand and debug
- **Serverless Deployments**: Better compatibility with managed databases
- **Small to Medium Applications**: Sufficient performance for most use cases
- **Learning Projects**: Easier to grasp for beginners
- **Production Stability**: More predictable behavior in managed environments

**Asynchronous is Better For:**
- **High-Concurrency Applications**: Thousands of simultaneous database operations
- **Real-time Applications**: WebSocket connections, live updates
- **Microservices**: Multiple concurrent API calls
- **Data Processing**: Large-scale ETL operations
- **Performance-Critical Applications**: Maximum throughput requirements

### LLM Chat: Async vs Sync Analysis

The AI chat functionality in FastOpp uses **asynchronous HTTP requests** to OpenRouter API, which is the correct approach. Here's why:

#### **Why LLM Chat Should Remain Async**

**1. HTTP Request Nature**
- **External API Calls**: Chat requests go to OpenRouter (external service)
- **Network Latency**: LLM responses can take 2-10 seconds
- **Non-blocking**: Other users can use the app while one user waits for LLM response
- **Timeout Handling**: Better control over request timeouts and retries

**2. User Experience Benefits**
- **Concurrent Users**: Multiple users can chat simultaneously
- **Responsive UI**: The interface remains responsive during LLM processing
- **Streaming Responses**: Can implement real-time response streaming
- **Error Isolation**: One user's LLM error doesn't affect others

**3. Technical Implementation**
```python
# ✅ CORRECT: Async for HTTP requests
async def chat_with_llama(user_message: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            return await response.json()

# ❌ WRONG: Sync for HTTP requests (blocks the entire server)
def chat_with_llama_sync(user_message: str):
    response = requests.post(url, json=payload)  # Blocks server
    return response.json()
```

#### **Database vs HTTP: Different Requirements**

| Aspect | Database Operations | HTTP Requests (LLM) |
|--------|-------------------|-------------------|
| **Location** | Local/Managed DB | External API |
| **Latency** | Milliseconds | Seconds |
| **Concurrency** | Limited by DB | High concurrency needed |
| **Error Handling** | Simple retry | Complex timeout/retry |
| **Best Pattern** | **Sync** (this version) | **Async** (correct) |

### Deployment Optimizations
- **LeapCell Tested**: Successfully deployed and tested on LeapCell platform
- **Health Checks**: Includes `/kaithheathcheck` endpoint for LeapCell health monitoring
- **Environment Variables**: Supports LeapCell's environment variable restrictions
- **File Storage**: Compatible with LeapCell's Object Storage for file persistence

### Performance Characteristics

**For This Application (Demo/Educational):**
- **Database Operations**: 10-50ms per operation (sync is fine)
- **LLM Requests**: 2-10 seconds per request (async is essential)
- **Concurrent Users**: 10-100 users (sync database + async HTTP works well)
- **Total Response Time**: Dominated by LLM latency, not database operations

**Conclusion**: The hybrid approach (sync database + async HTTP) is optimal for this use case.

### Code Modifications Summary

This version required extensive modifications to convert from async to sync database operations:

#### **Files Modified for Sync Database Operations**

**Core Database Files:**
- `db.py` - Changed from `AsyncSessionLocal` to `SessionLocal`, `create_async_engine` to `create_engine`
- `dependencies/database.py` - Updated session factory and dependency injection
- `dependencies/auth.py` - Removed `await` from database operations
- `dependencies/services.py` - Updated type hints from `AsyncSession` to `Session`

**Service Layer:**
- `services/webinar_service.py` - Converted all methods from async to sync
- `services/product_service.py` - Converted all methods from async to sync
- `services/chat_service.py` - **Remains async** (correct for HTTP requests)

**API Routes:**
- `routes/auth.py` - Removed `await` from database operations
- `routes/api.py` - Updated to call sync service methods
- `routes/webinar.py` - Updated to call sync service methods

**Scripts and Demo Data:**
- `oppdemo.py` - Converted initialization functions to sync
- `scripts/create_superuser.py` - Converted to sync
- `scripts/init_db.py` - Converted to sync
- `demo_scripts/add_test_users.py` - Converted to sync
- `demo_scripts/add_sample_products.py` - Converted to sync
- `demo_scripts/add_sample_webinars.py` - Converted to sync
- `demo_scripts/add_sample_webinar_registrants.py` - Converted to sync

#### **Dependencies Changed**

**Removed:**
- `asyncpg>=0.29.0` - Async PostgreSQL driver
- `sqlalchemy[asyncio]` - Async SQLAlchemy extensions

**Added:**
- `psycopg2-binary>=2.9.0` - Sync PostgreSQL driver
- Standard `sqlalchemy` - Sync SQLAlchemy

#### **What Remains Async (Correctly)**

**HTTP Requests (LLM Chat):**
- `services/chat_service.py` - All methods remain async for OpenRouter API calls
- `routes/chat.py` - Chat endpoints remain async
- Uses `aiohttp` for HTTP requests (not database operations)

**FastAPI Framework:**
- All FastAPI endpoints remain async (required by FastAPI)
- Middleware and dependency injection remain async
- Only database operations converted to sync

#### **Migration Strategy**

The conversion followed this systematic approach:

1. **Database Layer First**: Updated `db.py` and session factories
2. **Service Layer**: Converted all database service methods to sync
3. **API Layer**: Updated route handlers to call sync methods
4. **Scripts**: Converted all database initialization scripts
5. **Testing**: Verified each layer works before moving to the next

This approach ensured no broken intermediate states and maintained functionality throughout the conversion.

### Comparison with Django Async Operations

The original FastOpp project was created to address difficulties with mixing synchronous and asynchronous operations in Django. Now that we've implemented a hybrid approach in FastOpp, it's worth comparing how this solution compares to Django's async capabilities.

#### **Django's Async Limitations (Original Motivation)**

**The Problem FastOpp Was Designed to Solve:**
- **Mixed Sync/Async**: Django's ORM is synchronous, but LLM APIs require async HTTP requests
- **Context Switching**: Difficult to mix `async def` views with sync database operations
- **Error Handling**: Complex error handling across sync/async boundaries
- **Learning Curve**: Steep learning curve for developers familiar with Django patterns

**Django's Traditional Approach:**
```python
# ❌ PROBLEMATIC: Mixing sync and async in Django
def django_view(request):
    # Sync database operation
    user = User.objects.get(id=1)
    
    # Async HTTP request (requires special handling)
    import asyncio
    response = asyncio.run(async_llm_call(user.message))
    return JsonResponse({'response': response})
```

#### **Django's Modern Async Support (Django 4.1+)**

**Django Now Supports Async Views:**
```python
# ✅ Django 4.1+ async support
async def django_async_view(request):
    # Async database operations
    user = await User.objects.aget(id=1)
    
    # Async HTTP requests
    async with aiohttp.ClientSession() as session:
        response = await session.post(llm_url, json=payload)
        return JsonResponse({'response': await response.json()})
```

**Django's Async ORM Methods:**
- `Model.objects.aget()` - Async get
- `Model.objects.acreate()` - Async create
- `Model.objects.aupdate()` - Async update
- `Model.objects.adelete()` - Async delete
- `Model.objects.aexists()` - Async exists

#### **FastOpp vs Django Async Comparison**

| Aspect | **FastOpp (This Version)** | **Django Async** | **Django Sync** |
|--------|---------------------------|------------------|-----------------|
| **Database Operations** | Sync (Session) | Async (AsyncSession) | Sync (QuerySet) |
| **HTTP Requests** | Async (aiohttp) | Async (aiohttp) | Sync (requests) |
| **Learning Curve** | Moderate | Steep | Easy |
| **Serverless Compatibility** | Excellent | Good | Poor |
| **Debugging** | Easy | Complex | Easy |
| **Performance** | Good | Excellent | Limited |
| **Code Complexity** | Low | High | Low |

#### **When to Choose Each Approach**

**Choose FastOpp (This Version) When:**
- **Serverless Deployment**: LeapCell, Vercel, Netlify Functions
- **Educational Projects**: Learning FastAPI and async concepts
- **Small to Medium Apps**: 10-100 concurrent users
- **Mixed Operations**: Database + LLM APIs
- **Debugging Priority**: Need clear error messages and stack traces

**Choose Django Async When:**
- **High Concurrency**: Thousands of simultaneous operations
- **Real-time Features**: WebSockets, live updates
- **Performance Critical**: Maximum throughput required
- **Team Expertise**: Team comfortable with async patterns
- **Complex Workflows**: Multi-step async processes

**Choose Django Sync When:**
- **Traditional Web Apps**: CRUD operations, forms
- **Team Familiarity**: Team knows Django well
- **Simple Requirements**: Basic database operations
- **Legacy Systems**: Existing Django codebase

#### **FastOpp's Current Reality: Still Mixing Sync/Async**

**The Truth About FastOpp's Current State:**
FastOpp **still significantly mixes sync and async code**, just like Django. Here's the actual situation:

**1. FastAPI Framework Requirements:**
```python
# ✅ REQUIRED: All FastAPI endpoints must be async
async def get_products(product_service = Depends(get_product_service)):
    data = product_service.get_products_with_stats()  # Sync service call
    return JSONResponse(data)

async def chat_with_llm(request: Request):
    # Async HTTP request to LLM
    response = await ChatService.chat_with_llama(message)
    return JSONResponse(response)
```

**2. The Mixing Reality:**
- **FastAPI Endpoints**: All `async def` (required by FastAPI)
- **Database Operations**: Sync (our modification)
- **HTTP Requests**: Async (LLM chat)
- **Dependency Injection**: Mix of sync/async

**3. What We Actually Achieved:**
- **Database Layer**: Converted to sync (easier debugging)
- **Service Layer**: Converted to sync (simpler code)
- **HTTP Layer**: Remains async (necessary for LLM APIs)
- **Framework Layer**: Remains async (FastAPI requirement)

**4. The Real Benefits:**
- **Simpler Database Code**: No async/await in database operations
- **Easier Debugging**: Database errors are clearer
- **Better Serverless Compatibility**: Sync database connections work better
- **Reduced Complexity**: Less async context switching in database layer

**5. What We Still Have:**
- **Async Endpoints**: All FastAPI routes are async
- **Async HTTP**: LLM chat remains async
- **Mixed Dependencies**: Some sync, some async
- **Context Switching**: Still happens at FastAPI boundary

#### **Django's Async Evolution**

**Django 3.1+ (Limited Async):**
- Async views supported
- Limited async ORM support
- Complex async/sync mixing

**Django 4.1+ (Full Async ORM):**
- Complete async ORM support
- Async database operations
- Better async/sync integration

**Django 5.0+ (Enhanced Async):**
- Improved async performance
- Better async middleware support
- Enhanced async testing

**Django 6.0+ (Background Tasks - December 2025):**
- **Built-in Tasks Framework**: Native background task support
- **Task Decorator**: `@task` decorator for async operations
- **Queue Management**: Built-in task queuing and management
- **External Workers**: Tasks run in separate processes/services
- **LLM Integration**: Perfect for offloading LLM API calls to background

#### **Honest Assessment: FastOpp vs Django**

**The Reality Check:**
FastOpp **still has significant sync/async mixing**, just like Django. The key difference is **where** the mixing happens:

**FastOpp's Approach:**
- **Database Layer**: Sync (simpler, easier debugging)
- **HTTP Layer**: Async (necessary for LLM APIs)
- **Framework Layer**: Async (FastAPI requirement)
- **Mixing Point**: At FastAPI endpoint boundary

**Django's Approach:**
- **Database Layer**: Sync (traditional) or Async (Django 4.1+)
- **HTTP Layer**: Async (with aiohttp)
- **Framework Layer**: Sync (traditional) or Async (Django 3.1+)
- **Mixing Point**: Throughout the application

**✅ FastOpp's Actual Advantages:**
- **Simpler Database Code**: No async/await in database operations
- **Better Serverless Compatibility**: Sync database connections work better with managed databases
- **Easier Database Debugging**: Clearer error messages and stack traces
- **Reduced Database Complexity**: Less async context switching in database layer

**❌ What FastOpp Still Has:**
- **Sync/Async Mixing**: Still significant mixing at FastAPI boundary
- **Learning Curve**: Still need to understand both sync and async
- **Context Switching**: Still happens when calling sync services from async endpoints
- **Complexity**: Not as simple as pure sync Django

**✅ When FastOpp is Better:**
- **Serverless Deployments**: Better database connection handling
- **Managed Databases**: Works better with PostgreSQL-as-a-Service
- **Database-Heavy Apps**: Simpler database operations
- **Educational Projects**: Clearer separation of database vs HTTP concerns

**❌ When Django Might Be Better:**
- **Team Familiarity**: If team knows Django well
- **Traditional Web Apps**: CRUD operations without external APIs
- **Established Patterns**: Existing Django codebase and patterns
- **Full Async**: Django 4.1+ with full async ORM

**The Honest Conclusion:**
FastOpp doesn't eliminate sync/async mixing - it **reduces it in the database layer** where it matters most for serverless deployments. It's still a mixed approach, but with strategic benefits for specific use cases.

### Django 6.0 Background Tasks: Game Changer for LLM Integration

**Django 6.0's Background Tasks framework** (expected December 2025) fundamentally changes the Django vs FastOpp comparison for AI/LLM applications:

#### **Django 6.0's New Approach to LLM Integration**

**Traditional Django Problem:**
```python
# ❌ PROBLEMATIC: Blocking LLM calls in Django views
def django_view(request):
    user = User.objects.get(id=1)  # Sync database
    response = requests.post(llm_url, json=payload)  # Blocking HTTP
    return JsonResponse({'response': response.json()})
```

**Django 6.0 Solution:**
```python
# ✅ NEW: Background tasks for LLM operations
from django.tasks import task

@task
def process_llm_request(user_id, message):
    user = User.objects.get(id=user_id)  # Sync database
    response = requests.post(llm_url, json=payload)  # Background task
    return response.json()

def django_view(request):
    user = User.objects.get(id=1)  # Sync database
    task_id = process_llm_request.enqueue(user.id, message)  # Queue task
    return JsonResponse({'task_id': task_id, 'status': 'processing'})
```

#### **How This Changes the FastOpp vs Django Comparison**

| Aspect | **FastOpp (Current)** | **Django 6.0** | **Django 5.x and Earlier** |
|--------|---------------------|----------------|---------------------------|
| **Database Operations** | Sync (Session) | Sync (QuerySet) | Sync (QuerySet) |
| **LLM Integration** | Async HTTP in views | Background tasks | Blocking HTTP |
| **User Experience** | Real-time responses | Polling/WebSocket | Blocking requests |
| **Serverless Compatibility** | Excellent | Good | Poor |
| **Learning Curve** | Moderate | Easy | Easy |
| **Background Processing** | Manual (Celery) | Built-in | Manual (Celery) |

#### **Django 6.0's Advantages for LLM Applications**

**✅ What Django 6.0 Gains:**
- **Native Background Tasks**: No need for Celery or external task queues
- **Simpler LLM Integration**: `@task` decorator handles async operations
- **Better User Experience**: Non-blocking LLM requests
- **Familiar Patterns**: Django developers can use existing knowledge
- **Built-in Queue Management**: No external infrastructure needed

**✅ Perfect for LLM Use Cases:**
```python
# Django 6.0: Clean LLM integration
@task
def chat_with_llm(user_id, message):
    user = User.objects.get(id=user_id)
    response = requests.post(llm_url, json={
        'message': message,
        'user_context': user.profile
    })
    # Store response in database
    ChatLog.objects.create(user=user, message=message, response=response.json())
    return response.json()

def chat_view(request):
    if request.method == 'POST':
        message = request.POST['message']
        task = chat_with_llm.enqueue(request.user.id, message)
        return JsonResponse({'task_id': task.id, 'status': 'processing'})
```

#### **FastOpp's Remaining Advantages**

**✅ FastOpp Still Better For:**
- **Serverless Deployments**: Better compatibility with LeapCell, Vercel, Netlify
- **Real-time Responses**: Immediate LLM responses without polling
- **Simpler Architecture**: No external task workers needed
- **Educational Value**: Clear async/sync separation
- **FastAPI Ecosystem**: Modern async patterns and tooling

**✅ FastOpp's Approach:**
```python
# FastOpp: Real-time LLM responses
async def chat_with_llm(request: Request):
    user = get_current_user(request)  # Sync database
    response = await ChatService.chat_with_llama(message)  # Async HTTP
    return JSONResponse({'response': response})  # Immediate response
```

#### **Updated Recommendation Matrix**

**Choose Django 6.0 When:**
- **Traditional Web Apps**: CRUD operations with occasional LLM features
- **Background Processing**: Heavy LLM processing that can be queued
- **Team Familiarity**: Team knows Django well
- **Enterprise Applications**: Complex workflows with multiple background tasks
- **Polling/WebSocket**: Can implement real-time updates for task completion

**Choose FastOpp When:**
- **Serverless Deployment**: LeapCell, Vercel, Netlify Functions
- **Real-time LLM**: Immediate responses without polling
- **Educational Projects**: Learning modern async patterns
- **Simple LLM Integration**: Direct API calls without complex queuing
- **FastAPI Ecosystem**: Want to use modern Python web framework

#### **The New Landscape**

**Django 6.0 + Background Tasks** makes Django much more competitive for LLM applications, but FastOpp still has advantages for:

1. **Serverless Deployments**: Django's background tasks require external workers
2. **Real-time Responses**: FastOpp provides immediate LLM responses
3. **Simpler Architecture**: No need for task queue infrastructure
4. **Modern Patterns**: FastAPI's async-first approach

**The Bottom Line:**
Django 6.0's Background Tasks significantly narrows the gap, but FastOpp remains the better choice for serverless deployments and real-time LLM applications, while Django 6.0 becomes excellent for traditional web applications with background LLM processing.

### Long-Running Database Queries: A Critical Consideration

**Complex database queries can take 10+ seconds** and significantly impact the sync vs async decision:

#### **The Problem with Long Database Queries**

**Common Scenarios:**
- **Complex JOINs**: Multiple tables with large datasets
- **Analytics Queries**: Aggregations across millions of records
- **Data Processing**: ETL operations, data transformations
- **Reporting**: Complex business intelligence queries

**Example: E-commerce Analytics Dashboard**
```sql
-- Complex query: "Top 1000 products by revenue with customer demographics"
SELECT p.name, p.price, SUM(o.quantity) as total_sold,
       AVG(c.age) as avg_customer_age, COUNT(DISTINCT o.customer_id) as unique_customers
FROM products p
JOIN order_items oi ON p.id = oi.product_id
JOIN orders o ON oi.order_id = o.id
JOIN customers c ON o.customer_id = c.id
WHERE o.created_at >= '2024-01-01'
GROUP BY p.id, p.name, p.price
ORDER BY total_sold DESC
LIMIT 1000
```

#### **Synchronous Database (Current FastOpp) - The Problem**

**❌ Major Limitation:**
```python
# FastOpp (Sync) - BLOCKS the entire request
def get_analytics_report():
    # This query takes 10+ seconds
    result = session.execute(complex_analytics_query)
    return result.scalars().all()

async def analytics_endpoint(request: Request):
    # This blocks the entire FastAPI process for 10+ seconds
    data = get_analytics_report()  # 10+ second wait
    return JSONResponse({'data': data})
```

**Problems with Sync Approach:**
- **Blocks FastAPI**: Entire server process is blocked
- **No Concurrency**: Other requests must wait
- **Timeout Risk**: Serverless platforms may timeout
- **Poor User Experience**: 10+ second response times
- **Resource Waste**: Server idle while waiting for database

#### **Asynchronous Database (Original FastOpp) - Better for Long Queries**

**✅ Non-blocking Approach:**
```python
# Original FastOpp (Async) - NON-BLOCKING
async def get_analytics_report():
    # This query takes 10+ seconds but doesn't block other requests
    result = await session.execute(complex_analytics_query)
    return result.scalars().all()

async def analytics_endpoint(request: Request):
    # Other requests can be processed while this waits
    data = await get_analytics_report()  # 10+ second wait, but non-blocking
    return JSONResponse({'data': data})
```

**Benefits of Async Approach:**
- **Non-blocking**: Other requests can be processed
- **Concurrency**: Multiple long queries can run simultaneously
- **Better UX**: Server remains responsive
- **Serverless Friendly**: Works better with timeout limits
- **Resource Efficiency**: Server can handle other requests

#### **Query Performance Impact Matrix**

| Query Type | **Sync (Current FastOpp)** | **Async (Original FastOpp)** | **Background Tasks** |
|------------|---------------------------|------------------------------|---------------------|
| **Simple Queries** (< 100ms) | ✅ Perfect | ✅ Perfect | ❌ Overkill |
| **Medium Queries** (100ms-1s) | ✅ Good | ✅ Good | ❌ Overkill |
| **Long Queries** (1-10s) | ❌ Blocks server | ✅ Non-blocking | ✅ Best |
| **Very Long Queries** (10s+) | ❌ Timeout risk | ❌ Timeout risk | ✅ Essential |

#### **Better Solutions for Long Queries**

**1. Background Tasks (Recommended for 10s+ queries):**
```python
# FastOpp could implement background tasks
@task
def generate_analytics_report():
    result = session.execute(complex_analytics_query)
    return result.scalars().all()

async def analytics_endpoint(request: Request):
    task = generate_analytics_report.enqueue()
    return JSONResponse({'task_id': task.id, 'status': 'processing'})
```

**2. Caching Strategy:**
```python
# Cache expensive queries
@cache(ttl=3600)  # Cache for 1 hour
def get_analytics_report():
    result = session.execute(complex_analytics_query)
    return result.scalars().all()
```

**3. Database Optimization:**
```python
# Optimize the query itself
def get_analytics_report_optimized():
    # Use materialized views, indexes, query optimization
    result = session.execute(optimized_query)
    return result.scalars().all()
```

**4. Query Timeout Handling:**
```python
# Add timeout protection
def get_analytics_report_with_timeout():
    try:
        result = session.execute(complex_query, timeout=30)
        return result.scalars().all()
    except TimeoutError:
        # Fallback to cached data or simplified query
        return get_cached_analytics_data()
```

#### **Updated FastOpp vs Django Comparison**

**For Applications with Complex Database Queries:**

| Aspect | **FastOpp (Sync)** | **FastOpp (Async)** | **Django 6.0** |
|--------|-------------------|-------------------|----------------|
| **Simple Queries** | ✅ Excellent | ✅ Excellent | ✅ Excellent |
| **Long Queries** | ❌ Blocks server | ✅ Non-blocking | ✅ Background tasks |
| **Serverless** | ❌ Timeout risk | ✅ Better | ❌ Workers needed |
| **Real-time** | ❌ Poor UX | ✅ Good | ❌ Polling required |
| **Complexity** | ✅ Simple | ⚠️ Moderate | ⚠️ Moderate |

#### **Recommendations by Use Case**

**Choose Current FastOpp (Sync) When:**
- **Simple Applications**: Basic CRUD operations
- **Fast Queries**: All queries under 1 second
- **Serverless Deployment**: LeapCell, Vercel, Netlify
- **Educational Projects**: Learning FastAPI patterns

**Consider Reverting to Async When:**
- **Analytics Applications**: Complex reporting queries
- **Data Processing**: ETL operations
- **High Concurrency**: Multiple users with long queries
- **Performance Critical**: Need non-blocking database operations

**Consider Background Tasks When:**
- **Very Long Queries**: 10+ second database operations
- **Batch Processing**: Large data transformations
- **User Can Wait**: Polling/WebSocket acceptable
- **Dedicated Infrastructure**: Can run background workers

#### **The Honest Assessment**

**Long database queries (10+ seconds) are a significant consideration that favors async database operations.** The current FastOpp's sync approach works well for simple queries but has limitations for complex analytics and reporting queries.

**For applications with complex database queries, consider:**
1. **Reverting to async database operations** for the query layer
2. **Adding background task support** for long-running queries
3. **Implementing query optimization** strategies
4. **Using caching** for expensive queries
5. **Adding timeout protection** for query safety

**This is a valid concern that could influence the sync vs async decision** and should be considered when choosing between FastOpp's current sync approach and the original async approach.

### Database Concurrency: What Actually Happens with Multiple Users

**A common misconception**: People think that with synchronous database access, users have to wait in a queue for each query to complete. **This is not true!**

#### **Connection Pooling Solves the Queue Problem**

**You don't have to wait in a queue!** SQLAlchemy with psycopg2 creates a connection pool:

```python
# SQLAlchemy with psycopg2 creates a connection pool
engine = create_engine(
    "postgresql+psycopg2://...",
    pool_size=20,        # 20 concurrent connections
    max_overflow=30,     # Up to 30 additional connections
    pool_timeout=30,     # Wait max 30 seconds for connection
    pool_recycle=3600    # Recycle connections every hour
)
```

**What this means:**
- **20 people can query simultaneously** without waiting
- **Up to 50 total connections** (20 + 30 overflow) if needed
- **No queuing** until you exceed 50 concurrent users

#### **Real-World Example: 100 Users, 10-Second Queries**

Let's say you have 100 users trying to run 10-second analytics queries simultaneously:

**What actually happens:**
1. **First 20 users**: Get connections immediately, start their 10-second queries
2. **Users 21-50**: Get overflow connections, start their queries
3. **Users 51-100**: Wait in queue for a connection to become available
4. **After 10 seconds**: First batch finishes, connections become available
5. **Users 51-70**: Get connections, start their queries
6. **And so on...**

**Timeline:**
```
Time 0s:  Users 1-50 start queries
Time 10s: Users 1-50 finish, users 51-70 start
Time 20s: Users 51-70 finish, users 71-90 start
Time 30s: Users 71-90 finish, users 91-100 start
Time 40s: All users complete
```

#### **The Critical Difference: What Else Can Happen**

**Sync Database (Current FastOpp):**
```python
# While 50 users are running 10-second queries...
async def get_user_profile(user_id: int):
    # This ALSO has to wait for a database connection!
    with SessionLocal() as session:
        return session.get(User, user_id)
```

**Problem**: Even simple 100ms queries have to wait for connections occupied by 10-second queries.

**Async Database (Original FastOpp):**
```python
# While 50 users are running 10-second queries...
async def get_user_profile(user_id: int):
    # This can get a connection and complete in 100ms
    async with AsyncSessionLocal() as session:
        return await session.get(User, user_id)
```

**Benefit**: Simple queries don't get blocked by long-running queries.

#### **Connection Pool Exhaustion: The Real Bottleneck**

Here's what happens when you exceed your connection pool:

```python
# Connection pool settings
pool_size=20
max_overflow=30
# Total: 50 concurrent connections

# What happens with 100 concurrent users:
# - Users 1-50: Get connections, start queries
# - Users 51-100: Wait in queue (pool_timeout=30 seconds)
# - If timeout exceeded: ConnectionError
```

#### **Practical Solutions for High Concurrency**

**1. Increase Connection Pool Size:**
```python
engine = create_engine(
    "postgresql+psycopg2://...",
    pool_size=50,        # More concurrent connections
    max_overflow=100,    # More overflow capacity
    pool_timeout=60      # Longer timeout
)
```

**2. Use Celery for Long Queries (Recommended):**
```python
# FastAPI endpoint - returns immediately
async def analytics_endpoint(request: Request):
    task = process_analytics.delay(filters)
    return JSONResponse({'task_id': task.id})

# Celery worker - runs in background
@celery_app.task
def process_analytics(filters):
    with SessionLocal() as session:
        result = session.execute(complex_query)  # 10 seconds
        return result
```

**Benefits:**
- **No connection pool exhaustion** for web server
- **Web server stays responsive** for other requests
- **Celery workers** handle the heavy database work
- **Better resource management**

**3. Database Connection Limits:**
```sql
-- Check current connection limit
SHOW max_connections;  -- Usually 100-200 by default

-- Check current connections
SELECT count(*) FROM pg_stat_activity;
```

#### **The Honest Answer: What Actually Happens**

**With 100 users and 10-second queries:**

1. **First 20-50 users**: Start immediately (connection pool size)
2. **Remaining users**: Wait in queue for connections
3. **Web server**: May become unresponsive if all connections are busy
4. **Database**: Handles concurrent queries well (PostgreSQL is designed for this)
5. **User experience**: First batch gets results in 10s, others wait longer

**The real bottleneck is usually:**
- **Connection pool size** (not database performance)
- **Web server resources** (memory, CPU)
- **Network latency** (especially with cloud databases)

#### **Best Practice Recommendation for FastOpp + LeapCell**

```python
# 1. Optimize connection pool for your expected load
engine = create_engine(
    "postgresql+psycopg2://...",
    pool_size=20,        # Adjust based on expected concurrent users
    max_overflow=30,     # Allow burst capacity
    pool_timeout=30,     # Reasonable timeout
    pool_recycle=3600    # Prevent stale connections
)

# 2. Use Celery for long queries
@celery_app.task
def long_analytics_query(filters):
    with SessionLocal() as session:
        return session.execute(complex_query).scalars().all()

# 3. Keep sync database for fast queries
def get_user_data(user_id):
    with SessionLocal() as session:
        return session.get(User, user_id)
```

**This gives you:**
- **Responsive web server** for fast operations
- **Scalable background processing** for heavy operations
- **Efficient connection usage** without pool exhaustion
- **Better user experience** overall

**The key insight**: Connection pooling handles concurrency well, but long-running queries can still block your web server - which is why Celery is often the better solution for heavy database operations.

## Attribution

This project is a modified version of the original [FastOpp](https://github.com/Oppkey/FastOpp) project by [Oppkey](https://oppkey.com/). 

**Key Modifications:**
- **Database**: Switched from SQLite to PostgreSQL for better scalability
- **Architecture**: Converted to synchronous database operations for serverless compatibility
- **Deployment**: Optimized for LeapCell serverless platform
- **Education**: Enhanced documentation and tutorials for student learning

**Original FastOpp**: [https://github.com/Oppkey/FastOpp](https://github.com/Oppkey/FastOpp)

## Overview

Although both Django and Flask can absolutely be used for complex AI
applications and are great in many, many ways, there are often rough patches during
development of asynchronous AI applications that communicate with backend LLMs available
at OpenAI, Anthropic, and OpenRouter.

FastAPI has advantages in future-proof architecture, but can
have a steep learning curve for people, especially for
developers familiar with Django.

FastOpp provides an opinionated framework for FastAPI with the following features:

* admin panel similar to Django with role-based authentication
* SQL database with Django-inspired models and migrations
* Django-style HTML templates with modern UI components
  * Replaceable style templates to get started
* API endpoints to connect to other frontend frameworks
  * auto-generated documentation for API endpoints
  * designed to connect to Flutter and React in the future, but we do not have examples
* **oppman.py** core management tool for database, users, and application setup
* **oppdemo.py** demo file management tool for switching between demo and minimal modes

## Target Audience

This stack is opinionated and may not be for you. It is intended for students and novice developers who
know Python, but are not strong in or do not like JavaScript.

**FastOpp is not intended for production use or for experienced developers.**

* You strongly prefer Python over JavaScript on the backend
* You prefer to handle logic on the Python backend instead of using JavaScript code on the frontend
* You prefer inline styling instead of separation of concerns with CSS in separate files
* You prefer typed languages and want to use Python optional type hints instead of relying only on dynamic typing
* You prefer HTML files with Python code and variables embedded in the HTML instead of embedding HTML in the Python code on the server
* You are using Django or Flask and are having problems with async LLM communication
* You started with [Streamlit](https://streamlit.io/) or [Gradio](https://www.gradio.app/). Your code became more complex and is now difficult to manage

## Example Use Cases

* **University student** looking to build resume - Show potential employers that you can
  build an AI application. You want to host it cheaply and use cheap or free
  LLMs with the option
  to use a higher-quality LLM before you showoff your project.
  You have an idea on how to use AI and want to show it to people.
* **Hobbyist** looking to vibe code simple AI utility - Provide Cursor or equivalent
  access to demos and start with an opinionated structure for files and UI.
  Enforce vibe-code behavior with rules so that you can go back and edit your
  code. Deploy cheaply for less than $1 and month and scale up if your idea take off.
* **Small business entrepreneur** - You have
  great business ideas, but you are not a great programmer.
  You want to put AI into a business workflow that you are familiar with and show other
  people to get more help.

## FAQ and Concerns

### I'm concerned that this project is new and I don't want to waste time if it dies

The project is intended to teach use of FastAPI with LLMs.  The knowledge you gain will be
highly relevant to employers as long as Python and LLMs continue to be used together.
We intend that you eventually move off of Jinja2 templates and use the built-in API
for interfaces with React-variants or something like Flutter for mobile or web apps.
The project is intended to get you started on your path.  Even if it dies, your
knowledge will live on.

### I'm concerned about security

To be honest, we are not confident in the security architecture and model.  It is
sufficient for learning purposes, but you need to look into security yourself
and use another model if your project takes off.  FastOpp will get you started
quickly, but it is not intended for long-term production use.

### Should I use PostgreSQL instead of SQLite?

**This version uses PostgreSQL by default** and is optimized for managed PostgreSQL services like LeapCell. The synchronous database operations provide better reliability for serverless deployments.

**For the original FastOpp**: We use SQLite to get you started because there are less installation dependencies. If you use the database in production, we recommend switching to PostgreSQL.

### Should I use NGINX instead of serving the HTML templates from FastAPI?

Yes. We use FastAPI in deployment tutorials to get you started. NGINX is better.
FastAPI is very usable without NGINX if you do not have many simultaneous users.

### Should I change the LLM from LLama3.3-70b-instruct:free?

Yes. The free LLM is set for easy setup. We do not use it in production.  
At a minimum, you should
change this to the paid version of LLama3.3-70b-instruct or your
app will have very limited functionality.  If you password-protect your
app, you can control costs.  If only a few people use the app, the
free version will work.  LLama3.3-70b is pretty good, not great. It's primary
quality is that it is much cheaper than top-tier great LLMs like [GPT-5](https://openrouter.ai/openai/gpt-5).

### Can I use FastOpp in my own business?

Yes.  FastOpp itself is under the MIT license. You can modify FastOpp and close it off if that helps
your business or personal goals.  Refer to pyproject.toml for a list of FastOpp dependencies and confirm compliance for your use.

## Screenshots of Included Design Examples and Functionality Demos

FastOpp can be viewed as an opinionated design framework that adds an UI to an SQL
database (or vector db with extensions) and a UI to the input and
output of an LLM.

### Clickable Cards with Mouseover

![home](docs/images/readme/home.webp)

### Change Images Without Page Reload

![interactive](docs/images/interactive.webp)

### Hero

![hero](docs/images/readme/hero.webp)

### Database Admin List

![admin list](docs/images/admin.webp)

### Database Entry Edit

![edit](docs/images/edit.webp)

### User Management

![user management](docs/images/user_management.webp)

### User Authentication

Admin panel is restricted to logged-in users.

![authentication](docs/images/login.webp)

### Statistics Hero Card

![webinar top](docs/images/webinar_top.webp)

### People Hero Card

![webinar people](docs/images/webinar_people.webp)

### AI Chat with Cloud-Based LLM

![AI Chat](docs/images/ai_chat_indents.webp)

![AI Chat](docs/images/ai_chat.webp)

## Basic Design System and Reference Template

FastOpp comes with an optional basic UI design system to accelerate AI application development.

* based on Tailwind CSS, DaisyUI, AlpineJS and HTMX

## 🚀 Quick Start (For Students)

### Option 1: LeapCell Deployment (Recommended)

**Perfect for students** - Free serverless hosting with PostgreSQL:

1. **Fork this repository** on GitHub
2. **Deploy to LeapCell**:
   - Go to [leapcell.io](https://leapcell.io/)
   - Create new project
   - Connect your GitHub repository
   - Set environment variables (see [DEPLOYMENT.md](DEPLOYMENT.md))
   - Deploy and initialize database

3. **Access your app**: `https://your-app.leapcell.dev/`

### Option 2: Local Development

**For learning and development**:

### Prerequisites

* Python 3.12+
  If Python 3.12+ is not on your Mac, consider [installing pyenv](https://youtu.be/1F2IK7CU76U?feature=shared)
  and install the newest 3.12.x with pyenv. Although the latest stable Python is 3.13.7, we're using 3.12.x
  right now for maximum package compatibility.
* [uv](https://docs.astral.sh/uv/) package manager
* PostgreSQL (local installation)

## Educational Resources

- **📚 [Deployment Guide](DEPLOYMENT.md)**: Complete deployment instructions for all platforms
- **🤝 [Contributing Guide](CONTRIBUTING.md)**: How to contribute and learn from the codebase
- **🎓 [LeapCell Tutorial](DEPLOYMENT.md#leapcell-deployment)**: Step-by-step student deployment guide
- **🔧 [Local Development](DEPLOYMENT.md#local-development)**: Set up your development environment

## What you'll do

Use this guide to create your own repo from the FastOpp template, develop independently, and deploy. Do not open pull requests to the FastOpp repo.

* Create your own repo from the template
* Clone your repo locally
* Code, commit, and push to your repo

### 1. Create your repo from the template

1. Open this repo: `https://github.com/Oppkey/FastOpp`
2. Click blue button, upper right, called **Use this template** → **Create a new repository**
3. Name it (e.g., `fastopp-<yourproject>`)
4. Choose Public
5. Click **Create repository from template**

> Result: you now have your **own** repo. It is **not** a fork of FastOpp.

### 2. Clone your repo

```bash
git clone https://github.com/<YOUR_USERNAME>/fastopp-<yourproject>.git
cd fastopp-<yourproject>

# Install dependencies
uv sync
```

### 3. Environment Configuration

Create a `.env` file in your project root:

**Required Environment Variables:**

* `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql+psycopg2://user:pass@host:port/db`)
* `SECRET_KEY`: Secret key for JWT tokens and session management
* `ENVIRONMENT`: Set to "development" for development mode
* `OPENROUTER_API_KEY`: API key for OpenRouter (required for AI demo features)

**Optional Environment Variables:**

* `UPLOAD_DIR`: Directory for storing uploaded files (defaults to `static/uploads` if not set)
  * **Local Development**: Not set (uses default `static/uploads`)
  * **Production Deployments**: Set to persistent storage path (e.g., `/data/uploads`, `/app/uploads`)
  * **URL Compatibility**: Files are always served from `/static/uploads/photos/` regardless of storage location

#### Generate Secure SECRET_KEY

**Recommended**: Use the built-in secret generator for maximum security:

```bash
# Generate a cryptographically secure SECRET_KEY
uv run python oppman.py secrets
```

This will output a line like `SECRET_KEY=...` that you can copy directly into your `.env` file.

**Alternative methods:**

```bash
# Create environment file with secure defaults
cat > .env << EOF
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/fastopp_db
SECRET_KEY=$(uv run python oppman.py secrets | grep SECRET_KEY | cut -d'=' -f2)
ENVIRONMENT=development
OPENROUTER_API_KEY=your_openrouter_api_key_here
EOF
```

**Or manually create `.env`:**

```bash
# .env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/fastopp_db
SECRET_KEY=your_generated_secret_key_here
ENVIRONMENT=development
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

**⚠️ Security Important:**

* Never commit `.env` files to version control
* Add `.env` to your `.gitignore` file
* Keep your SECRET_KEY secure and private
* Use different SECRET_KEYs for different environments

### 4. One-Command Setup

```bash
# Complete setup with one command
uv run python oppdemo.py init
```

This single command will:

* Initialize migrations
* Create initial migration
* Apply migrations
* Initialize database with sample data
* Create superuser and test data

#### Alternative: Step-by-Step Setup

If you prefer to understand each step:

```bash
# Initialize migrations (first time only)
uv run python oppman.py migrate init

# Create initial migration
uv run python oppman.py migrate create "Initial migration"

# Apply migrations
uv run python oppman.py migrate upgrade

# Initialize database with sample data
uv run python oppdemo.py init
```

**Note**: Demo data initialization commands have been moved from `oppman.py` to `oppdemo.py` for better separation of concerns.

### 5. Start Development Server

```bash
# Start the server
uv run python oppman.py runserver
```

### 5. Access the Application

Visit these URLs in your browser:

* **Homepage**: `http://localhost:8000/`
* **Admin Panel**: `http://localhost:8000/admin/`
* **API Docs**: `http://localhost:8000/docs`

#### Admin Panel Login

Use these credentials to access the admin panel:

* **Email**: `admin@example.com`
* **Password**: `admin123`

## 🛠️ Management Commands

FastOpp now uses two separate management tools for better organization and separation of concerns:

### Core Application Management (oppman.py)

**oppman.py** is similar to Django's manage.py and focuses on core application management:

```bash
# Server management
uv run python oppman.py runserver       # Start development server
uv run python oppman.py stopserver      # Stop development server
uv run python oppman.py production      # Start production server

# Database management
uv run python oppman.py backup          # Backup database
uv run python oppman.py delete          # Delete database (with backup)

# Migration management
uv run python oppman.py migrate init    # Initialize migrations
uv run python oppman.py migrate create "Add new table"  # Create migration
uv run python oppman.py migrate upgrade # Apply migrations
uv run python oppman.py migrate current # Check migration status

# Environment and utilities
uv run python oppman.py env             # Check environment configuration
uv run python oppman.py secrets         # Generate SECRET_KEY for .env file
uv run python oppman.py demo            # Show demo command help
uv run python oppman.py help            # Show comprehensive help
```

### Demo Management (oppdemo.py)

**oppdemo.py** handles all demo-related functionality:

```bash
# Demo file management
uv run python oppdemo.py save           # Save demo files to demo_assets
uv run python oppdemo.py restore        # Restore demo files from backup
uv run python oppdemo.py destroy        # Switch to minimal application
uv run python oppdemo.py diff           # Show differences between current and backup
uv run python oppdemo.py backups        # List all available backups

# Demo data initialization (moved from oppman.py)
uv run python oppdemo.py init           # Complete initialization (database + superuser + users + products + webinars + registrants)
uv run python oppdemo.py db             # Initialize database only
uv run python oppdemo.py superuser      # Create superuser only
uv run python oppdemo.py users          # Add test users only
uv run python oppdemo.py products       # Add sample products only
uv run python oppdemo.py webinars       # Add sample webinars only
uv run python oppdemo.py download_photos # Download sample photos
uv run python oppdemo.py registrants    # Add sample registrants
uv run python oppdemo.py clear_registrants # Clear and add fresh registrants
uv run python oppdemo.py check_users    # Check existing users
uv run python oppdemo.py test_auth      # Test authentication
uv run python oppdemo.py change_password # Change user password
uv run python oppdemo.py list_users     # List all users

# Help
uv run python oppdemo.py help           # Show comprehensive help
```

### Server Management

```bash
# Development server
uv run python oppman.py runserver       # Start development server
uv run python oppman.py stopserver      # Stop development server

# Production server (optional)
uv run python oppman.py production      # Start production server
```

### Migration Management

```bash
# Initialize migrations (first time only)
uv run python oppman.py migrate init

# Create new migration
uv run python oppman.py migrate create "Add new table"

# Apply migrations
uv run python oppman.py migrate upgrade

# Check migration status
uv run python oppman.py migrate current

# View migration history
uv run python oppman.py migrate history
```

### Environment Management

```bash
# Check environment configuration
uv run python oppman.py env

# Generate secure SECRET_KEY for .env file
uv run python oppman.py secrets

# Show all available commands
uv run python oppman.py help
```

### Backup Management

Backup files are automatically organized in the `backups/` directory:

* **`backups/destroy/`** - Files backed up before switching to minimal mode
* **`backups/restore/`** - Files backed up before restoring demo mode

Each backup includes a timestamp for easy identification. Use `uv run python oppdemo.py backups` to list all available backups.

## 📊 Test Data

The application comes with pre-loaded test data:

### Users

* **Superuser**: `admin@example.com` / `admin123`
* **Test Users**: `john@example.com`, `jane@example.com`, `bob@example.com` / `test123`

### Products

Sample products with various categories and prices for testing the admin interface.

## 🛠️ Tool Separation

FastOpp now uses two separate management tools for better organization and separation of concerns:

### oppman.py - Core Application Management

**oppman.py** is similar to Django's manage.py and focuses on core application management:

* **Server Management**: Start/stop development and production servers
* **Database Management**: Backup, delete, and migration operations
* **Environment Management**: Configuration checks and utilities
* **Core Operations**: Essential application lifecycle management

### oppdemo.py - Demo Management

**oppdemo.py** handles all demo-related functionality:

* **Demo File Management**: Save/restore demo state, switch between demo and minimal modes
* **Demo Data Initialization**: All sample data creation (users, products, webinars, registrants)
* **Demo State Control**: Comprehensive demo application management

## 🔄 Database Migrations

### Migration Workflow

1. **Add/Modify Models**: Edit `models.py` with your changes
2. **Create Migration**: `uv run python oppman.py migrate create "Description"`
3. **Review Migration**: Check the generated file in `alembic/versions/`
4. **Apply Migration**: `uv run python oppman.py migrate upgrade`
5. **Verify**: `uv run python oppman.py migrate current`

## 🚨 Troubleshooting

### Common Issues

1. **"Alembic not found"**

   ```bash
   uv add alembic
   ```

2. **"Alembic not initialized"**

   ```bash
   uv run python oppman.py migrate init
   ```

3. **Environment issues**

     ```bash
     # Check environment configuration
     uv run python oppman.py env
     ```

4. **Database issues**

     ```bash
     # Backup and reset
     uv run python oppman.py backup
     uv run python oppman.py delete
     uv run python oppman.py init
     ```

5. **"Module not found" errors**

   ```bash
   # Reinstall dependencies
   uv sync
   ```

6. **Port already in use**

    ```bash
    # Stop any running servers
    uv run python oppman.py stopserver
    
    or
    
    # Kill uvicorn processes manually
    pkill -f uvicorn

    or
     
    # use a different port
    uv run uvicorn main:app --reload --port 8001
    ```

### Quick Reset

FastOpp is a learning tool designed for tinkering, you can play around
with the demo and then restore the entire demo or just the database to a working state:

```bash
# Backup current database
uv run python oppman.py backup

# Delete database and reinitialize
uv run python oppman.py delete # delete SQL database

# initialize blank database
uv run python oppdemo.py db

or

# initializes and puts in fake data
uv run python oppdemo.py init 

# Verify setup
uv run python oppman.py env
```

## 📁 File Uploads and Storage

FastOpp includes a flexible file upload system that works across different deployment environments:

### How It Works

* **Local Development**: Files stored in `static/uploads/` directory (default behavior)
* **Production Deployments**: Files stored in configurable directory via `UPLOAD_DIR` environment variable
* **URL Consistency**: All uploads served from `/static/uploads/photos/` regardless of storage location

### Configuration Examples

```bash
# Local development (no environment variable needed)
# Files stored in: static/uploads/photos/
# URLs served from: /static/uploads/photos/

# Docker deployment
UPLOAD_DIR=/app/uploads
# Files stored in: /app/uploads/photos/
# URLs served from: /static/uploads/photos/

# Fly.io deployment with persistent Fly Volume mounted at /data
UPLOAD_DIR=/data/uploads
# Files stored in: /data/uploads/photos/
# URLs served from: /static/uploads/photos/

# Kubernetes deployment
UPLOAD_DIR=/persistent/uploads
# Files stored in: /persistent/uploads/photos/
# URLs served from: /static/uploads/photos/
```

### Benefits

* **Environment-agnostic**: Works in any deployment environment
* **Backward compatible**: Local development unchanged
* **Persistent storage**: Production deployments can use persistent volumes
* **URL consistency**: Frontend code doesn't need to change

## 🔄 Demo vs Minimal Mode

FastOpp supports two application modes:

### Demo Mode (Default)

* Full-featured application with AI chat, dashboard, design examples
* Sample data and comprehensive UI components
* Ideal for learning and showcasing features

### Minimal Mode

* Basic FastAPI application with authentication
* Clean slate for building your own application
* Includes admin panel and basic structure with password-protected pages

### Switching Between Modes

```bash
# Save current demo state
uv run python oppdemo.py save

# Switch to minimal mode
uv run python oppdemo.py destroy

# Restore demo mode
uv run python oppdemo.py restore

# Check what's different
uv run python oppdemo.py diff
```

## 🚀 LeapCell Deployment

This version has been specifically tested and optimized for deployment on [LeapCell](https://leapcell.io/), a serverless platform that provides:

- **Managed PostgreSQL Database** with automatic SSL configuration
- **Object Storage** for file persistence
- **Async Task Processing** for background operations
- **Health Check Endpoints** for platform monitoring

### LeapCell-Specific Features

- **Health Check Endpoint**: `/kaithheathcheck` for LeapCell platform monitoring
- **Database URL Conversion**: Automatically converts `postgresql+asyncpg://` to `postgresql+psycopg2://`
- **SSL Configuration**: Proper SSL handling for managed PostgreSQL
- **Connection Pooling**: Optimized for serverless environments
- **File Backup/Restore**: Object Storage integration for file persistence

### Deployment Steps

1. **Create LeapCell Project**: Set up a new project on LeapCell
2. **Configure Environment Variables**:
   ```bash
   DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db  # LeapCell provides this
   SECRET_KEY=your_secure_secret_key
   ENVIRONMENT=production
   S3_ACCESS_KEY=your_leapcell_s3_key
   S3_SECRET_KEY=your_leapcell_s3_secret
   ```
3. **Deploy**: Push your code to LeapCell
4. **Initialize**: Use the `/async/init-demo` endpoint to set up the database

### Testing

The deployment has been verified to work with:
- ✅ Database initialization and migrations
- ✅ User authentication and management
- ✅ File uploads and Object Storage backup
- ✅ AI chat functionality
- ✅ Admin panel access

## 📚 Documentation

### Courseware - YouTube Video Tutorials

* [FastAPI for AI LLM Apps with SQLAdmin, SQLModel - Quickstart Template for Frontend](https://youtu.be/_P9p0BGO64Q) - published August 15, 2025
* [FastAPI with LLM and Database Beginner Tutorial](https://youtu.be/_NlY0zlcC6Q) - published August 18, 2025
* [Deploy FastAPI and SQLite to Fly for Cheap Hosting](https://youtu.be/k-6xxE6k7Fs) - published August 26, 2025
* [Permanent Photo Uploads on Fly with FastAPI Static Files on Fly Volume](https://youtu.be/YKC3ZSA2Eh8) - published August 29, 2025
* [Free FastAPI Deployment - No Credit Card - Railway](https://youtu.be/7vxroD-tyo8) - published Sept 3, 2025

### Tutorials

* [Add new page](docs/tutorials/add_new_page.md)
* [Change LLM](docs/tutorials/change_llm.md)

### Deployment

* [Deploy to fly.io](docs/deployment/FLY_DEPLOYMENT.md)
* [fly deployment costs discussion](https://github.com/Oppkey/fastopp/discussions/25)

### Architecture and Overview

* [Architecture Overview](docs/ARCHITECTURE.md) - MVS Architecture and code organization
* [Database](docs/DATABASE.md)
* [Authentication](docs/AUTHENTICATION.md)
* [Features](docs/FEATURES.md)

## Guidelines

* beautiful
* cheap
* easy
* opinionated
