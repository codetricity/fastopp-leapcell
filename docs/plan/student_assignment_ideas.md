# Student Assignment: Fake Data Generator for Event Attendees

## Overview

This assignment teaches students to build a comprehensive fake data generation system for event attendees, progressing from a command-line tool to a full web application using FastOpp. The project culminates in creating both a data generator and a query interface that demonstrates LLM integration with SQL databases.

## Learning Objectives

- Build command-line Python applications
- Integrate with LLMs for data generation
- Create web interfaces using FastOpp
- Work with CSV data and SQL databases
- Implement vector databases for embeddings
- Query databases and process results with LLMs

## Student Benefits

### Portfolio and Career Development

**Showcase Skills to Employers:**

- **Live Web Application**: Students will have a fully functional web application they can demonstrate to potential employers
- **Modern Tech Stack**: Demonstrates proficiency with FastAPI, LLMs, SQL databases, and vector databases
- **Real-World Problem Solving**: Shows ability to build practical tools that solve actual business needs
- **Full-Stack Development**: Combines backend API development with frontend web interfaces

**Community and Peer Recognition:**

- **Open Source Potential**: The fake data generator can be shared with the developer community
- **Useful Tool**: Other developers can use the tool for their own testing and development needs
- **GitHub Portfolio**: Creates impressive repository with working code, documentation, and demos
- **Technical Blogging**: Students can write about their experience with LLM integration and vector databases

### Technical Skill Demonstration

**Advanced Technologies:**

- **LLM Integration**: Shows experience with AI/ML APIs and prompt engineering
- **Vector Databases**: Demonstrates knowledge of FAISS and semantic search capabilities
- **SQL Database Design**: Shows ability to design efficient database schemas and queries
- **API Development**: Demonstrates RESTful API design and implementation
- **Web Scraping/Integration**: Experience with external APIs (Unsplash, generated.photo)

**Extensibility and Scalability:**

- **Database Connectors**: Easy to extend for different database types (PostgreSQL, MongoDB, etc.)
- **Modular Architecture**: Clean separation of concerns makes the code maintainable and extensible
- **Performance Optimization**: Experience with batch processing and large dataset handling
- **Error Handling**: Robust error handling and logging systems

### Practical Business Value

**Real-World Applications:**

- **Testing Data**: Generates realistic test data for software development
- **Prototype Development**: Useful for rapid prototyping and MVP development
- **Data Analysis**: Demonstrates ability to query and analyze large datasets
- **Business Intelligence**: Shows understanding of data-driven decision making

**Feedback and Collaboration:**

- **User Feedback**: Opportunity to get feedback from other developers using the tool
- **Open Source Contributions**: Potential for community contributions and improvements
- **Documentation Skills**: Practice writing clear, comprehensive documentation
- **Version Control**: Experience with Git workflows and collaborative development

### Career Advancement Opportunities

**Resume Building:**

- **Project Portfolio**: Tangible evidence of technical skills and problem-solving ability
- **Code Quality**: Demonstrates ability to write clean, well-documented code
- **System Design**: Shows understanding of database design and API architecture
- **Testing**: Experience with data validation and quality assurance

**Interview Talking Points:**

- **Technical Challenges**: Can discuss LLM integration challenges and solutions
- **Performance Optimization**: Experience with handling large datasets efficiently
- **User Experience**: Understanding of web interface design and user needs
- **Problem Solving**: Real examples of identifying and solving technical problems

## Assignment Structure

### Phase 1: Command-Line Data Generator

#### 1.1 Basic Single Person Generator

**Requirements:**

- Create a Python script that generates one fake event attendee
- Use an LLM (OpenAI, Anthropic, or local model) to generate realistic data
- Include fields: name, email, attendance time, event name, job_title, company, industry (from email domain analysis)
- Mix of Gmail and corporate email addresses
- Generate realistic professional distributions based on event type
- Output to CSV format

**Deliverables:**

- `generate_attendee.py` - Single person generator
- Sample CSV output with one record
- Documentation of LLM prompts used

**Technical Requirements:**

- Use environment variables for API keys
- Handle API rate limits and errors
- Validate generated data format

#### 1.2 Batch Data Generation

**Requirements:**

- Extend to generate 20 fake attendees per batch
- Implement specific targets: 1000 and 5000 attendees
- Add progress tracking and error handling
- Support different event types
- Optimize for larger datasets

**Deliverables:**

- `batch_generator.py` - Batch generation script
- Configuration file for different event types
- Logging system for generation process
- Performance benchmarks for 1000 and 5000 attendee generation

#### 1.3 Image Integration

**Requirements:**

- Integrate with Unsplash API for fake people images
- Alternative: Use generated.photo/faces API
- Download and store images locally
- Link images to attendee records
- Handle image download failures gracefully

**Deliverables:**

- `image_downloader.py` - Image fetching module
- Image storage system
- Updated CSV with image file paths

### Phase 2: Web Interface with FastOpp

#### 2.1 FastOpp Integration

**Requirements:**

- Use FastOpp base assets to create web interface
- Build forms for data generation parameters
- Implement real-time generation progress
- Add download functionality for generated CSV

**Deliverables:**

- FastOpp-based web application
- User interface for data generation
- CSV download functionality

#### 2.2 Advanced Configuration Options

**Requirements:**

- Event name input field
- Number of attendees with preset buttons: 1, 1000, 5000
- Corporate vs Gmail ratio slider
- Product interest categories
- Booth assignment options
- Date range for attendance times
- Performance indicators for different dataset sizes

**Deliverables:**

- Interactive web form
- Real-time preview of generation parameters
- Batch processing with progress bars
- Time estimates for 1000 and 5000 attendee generation

#### 2.3 Data Export and Management

**Requirements:**

- CSV export with custom naming
- JSON export option
- Database import functionality
- Data validation and cleaning
- Bulk operations (delete, regenerate)

**Deliverables:**

- Export system
- Database integration
- Data management interface

### Phase 3: Database Integration and Query Interface

#### 3.1 SQL Database Setup

**Requirements:**

- Create SQLite/PostgreSQL database schema
- Import CSV data into database
- Design efficient queries for attendee data
- Implement search and filtering

**Deliverables:**

- Database schema design
- Import scripts
- Query interface

#### 3.2 LLM Query Interface

**Requirements:**

- Build interface to query database with natural language
- Convert natural language to SQL queries
- Process query results with LLM
- Generate insights and summaries

**Example Queries:**

- "How many people are interested in Docker?"
- "What are the most popular product categories?"
- "Show me attendees from AWS security companies"
- "Generate a report on attendee demographics"
- "What industries are most represented at the event?"
- "How many attendees are from startups vs enterprises?"
- "What job titles are most common among attendees?"
- "Which companies have the most attendees?"
- "What product categories are most popular?"

**Deliverables:**

- Natural language query interface
- SQL generation system
- LLM result processing
- Query history and favorites

#### 3.3 Vector Database Integration

**Requirements:**

- Implement FAISS vector database
- Create embeddings for attendee data
- Build semantic search capabilities
- Enable similarity-based queries

**Deliverables:**

- Vector database setup
- Embedding generation system
- Semantic search interface
- Similarity query examples


## Technical Implementation Details

### Data Schema

```sql
CREATE TABLE attendees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    company TEXT,
    event_name TEXT NOT NULL,
    attendance_time TIMESTAMP,
    job_title TEXT,
    industry TEXT,
    company_size TEXT, -- inferred from company name/domain
    product_interests TEXT,
    booth_visited TEXT,
    image_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Realistic Data Collection Strategy

**What We Can Realistically Collect:**
- **Name and Email**: Standard registration information
- **Company**: Often provided in email signature or inferred from email domain
- **Job Title**: Sometimes provided during registration or inferred from company/industry
- **Industry**: Can be inferred from company name, email domain, or job title
- **Company Size**: Can be inferred from company name patterns (e.g., "TechCorp" vs "StartupXYZ")
- **Product Interests**: Can be inferred from booth visits or job title
- **Booth Visits**: Tracked through badge scanning or check-in systems

**What We Cannot Realistically Collect:**
- Age, gender, personal demographics (not typically collected at events)
- Detailed personal information
- Salary or compensation data

### LLM Integration Points

1. **Data Generation Prompts:**
   - Generate realistic names and emails
   - Create believable company names and job titles
   - Infer industry from company name/email domain
   - Infer company size from company name patterns
   - Generate product interests based on job title/industry
   - Create realistic attendance times
   - Generate booth visits based on product interests

2. **Query Processing:**
   - Convert natural language to SQL
   - Summarize query results
   - Generate insights from data
   - Create reports and visualizations

### API Integrations

1. **Unsplash API:**
   - Search for people images
   - Download and store images
   - Handle rate limits

2. **Generated.photo API:**
   - Alternative image source
   - Batch image generation
   - Custom image parameters

3. **LLM APIs:**
   - OpenAI GPT models
   - Anthropic Claude
   - Local models (Ollama)

## Assessment Criteria

### Phase 1 (40 points)

- Command-line tool functionality (15 points)
- LLM integration quality (10 points)
- Code organization and documentation (10 points)
- Error handling and robustness (5 points)


### Phase 2 (30 points)

- FastOpp integration (10 points)
- User interface design (10 points)
- Configuration options (5 points)
- Export functionality (5 points)


### Phase 3 (30 points)

- Database integration (10 points)
- LLM query processing (10 points)
- Vector database implementation (5 points)
- Overall system integration (5 points)


## Deliverables Timeline

### Week 1-2: Phase 1

- Basic single person generator
- Batch generation system (1000 and 5000 attendees)
- Image integration


### Week 3-4: Phase 2

- FastOpp web interface
- Advanced configuration with preset buttons
- Export system


### Week 5-6: Phase 3

- Database integration
- LLM query interface
- Vector database setup


## Bonus Features

- **Data Visualization:** Create charts and graphs of generated data
- **API Endpoints:** Build REST API for data generation
- **Authentication:** Add user authentication and data ownership
- **Scheduling:** Implement scheduled data generation
- **Analytics:** Track usage and generation statistics
- **Multi-language Support:** Generate data in different languages

## Resources and References

- [FastOpp Documentation](../README.md)
- [Unsplash API Documentation](https://unsplash.com/developers)
- [Generated.photo API](https://generated.photos/)
- [FAISS Documentation](https://faiss.ai/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Success Metrics

- Generate single attendee in under 10 seconds
- Generate 1000 realistic attendees in under 5 minutes
- Generate 5000 realistic attendees in under 15 minutes
- Web interface responds to user input in under 2 seconds
- LLM queries return relevant results 90%+ of the time
- System handles errors gracefully without crashing
- Code is well-documented and maintainable
