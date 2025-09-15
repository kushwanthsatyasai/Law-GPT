# Legal Database Integration & Persistent Chat System

## Overview

The Law-GPT application now includes comprehensive legal database integration and persistent chat functionality, enabling users to:

- **Research Case Law**: Search through legal precedents and court decisions
- **Access Legal Statutes**: Find relevant legislation and regulations
- **Persistent Conversations**: Save and resume chat sessions
- **Hybrid Search**: Combine document analysis with legal database research
- **Context-Aware Responses**: AI responses that reference both user documents and legal databases

## 🏛️ **Legal Database Integration**

### **Supported Legal Databases**

1. **CanLII (Canadian Legal Information Institute)**
   - Free access to Canadian case law and legislation
   - API integration for real-time searches
   - Comprehensive coverage of federal and provincial law

2. **BAILII (British and Irish Legal Information Institute)**
   - Free access to British and Irish case law
   - Web scraping integration for case searches
   - Extensive collection of legal precedents

3. **Local Database Storage**
   - Cached legal data for faster searches
   - Persistent storage of frequently accessed cases
   - Offline access to previously searched content

### **Search Capabilities**

- **Case Law Search**: Find relevant court decisions and precedents
- **Statute Search**: Locate applicable legislation and regulations
- **Jurisdiction Filtering**: Search by specific legal jurisdictions
- **Relevance Scoring**: AI-powered relevance ranking
- **Citation Tracking**: Full legal citation information

## 💬 **Persistent Chat System**

### **Chat Session Management**

- **Session Creation**: Create named chat sessions for different topics
- **Message History**: Complete conversation history with timestamps
- **Session Organization**: Sidebar with all active chat sessions
- **Session Deletion**: Soft delete with confirmation
- **Session Renaming**: Update session titles as needed

### **Message Types**

1. **Text Messages**: Standard conversational messages
2. **Legal Research**: Messages that trigger legal database searches
3. **Document Analysis**: Messages related to uploaded documents
4. **Hybrid Search**: Messages combining document and legal database search

### **AI Response Intelligence**

- **Context Awareness**: AI remembers conversation history
- **Source Integration**: References both user documents and legal databases
- **Response Types**: Different response formats based on query type
- **Metadata Tracking**: Rich metadata for each response

## 🔧 **Technical Implementation**

### **Database Schema**

#### **Chat Sessions Table**
```sql
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);
```

#### **Chat Messages Table**
```sql
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES chat_sessions(id),
    role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text',
    metadata TEXT, -- JSON string for additional data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **Legal Cases Table**
```sql
CREATE TABLE legal_cases (
    id SERIAL PRIMARY KEY,
    case_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    court VARCHAR(200) NOT NULL,
    jurisdiction VARCHAR(100) NOT NULL,
    case_date TIMESTAMP WITH TIME ZONE,
    case_type VARCHAR(100) NOT NULL,
    summary TEXT NOT NULL,
    full_text TEXT NOT NULL,
    keywords TEXT, -- comma-separated keywords
    citation VARCHAR(200) NOT NULL,
    source VARCHAR(100) NOT NULL, -- 'canlii', 'bailii', etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **Legal Statutes Table**
```sql
CREATE TABLE legal_statutes (
    id SERIAL PRIMARY KEY,
    statute_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    jurisdiction VARCHAR(100) NOT NULL,
    section_number VARCHAR(50),
    statute_text TEXT NOT NULL,
    summary TEXT NOT NULL,
    keywords TEXT, -- comma-separated keywords
    effective_date TIMESTAMP WITH TIME ZONE,
    source VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **API Endpoints**

#### **Chat Management**
- `POST /chat/sessions` - Create new chat session
- `GET /chat/sessions` - Get user's chat sessions
- `GET /chat/sessions/{id}` - Get detailed chat session
- `POST /chat/sessions/{id}/messages` - Send message
- `DELETE /chat/sessions/{id}` - Delete chat session
- `PUT /chat/sessions/{id}/rename` - Rename chat session

#### **Legal Research**
- `POST /legal-research` - Search legal databases
- `POST /hybrid-query` - Combined document and legal search

### **Services Architecture**

#### **ChatService**
- Manages chat sessions and messages
- Handles AI response generation
- Integrates with legal database service
- Manages conversation context

#### **LegalDatabaseService**
- Interfaces with external legal APIs
- Manages local legal data storage
- Handles search and relevance scoring
- Provides data caching and persistence

## 🚀 **Usage Examples**

### **1. Legal Research Query**
```
User: "What are the recent cases about employment termination in Canada?"

AI Response: 
- Searches CanLII for Canadian employment law cases
- Finds relevant precedents and court decisions
- Provides case summaries and citations
- Explains legal principles and implications
```

### **2. Document Analysis with Legal Context**
```
User: "Analyze this employment contract and tell me about termination clauses"

AI Response:
- Analyzes the uploaded document for termination clauses
- Searches legal databases for relevant case law
- Compares document clauses with legal precedents
- Provides safety assessment and recommendations
```

### **3. Hybrid Legal Research**
```
User: "How does this NDA compare to standard practices in intellectual property law?"

AI Response:
- Analyzes the uploaded NDA document
- Searches for IP law precedents and statutes
- Compares document terms with legal standards
- Provides comprehensive legal analysis
```

## 📱 **Frontend Features**

### **Chat Interface**
- **Sidebar Navigation**: List of all chat sessions
- **Message History**: Complete conversation history
- **Message Types**: Visual indicators for different message types
- **Real-time Updates**: Live message updates
- **Session Management**: Create, rename, delete sessions

### **Legal Research Integration**
- **Search Results**: Display cases and statutes with relevance scores
- **Citation Information**: Full legal citations and court details
- **Source Attribution**: Clear indication of data sources
- **Relevance Filtering**: Sort by relevance and date

### **Enhanced Dashboard**
- **Chat Access**: Quick access to legal chat interface
- **Document Integration**: Seamless connection between documents and chat
- **Session Overview**: Recent chat sessions in sidebar

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Legal Database API Keys
CANLII_API_KEY=your_canlii_api_key
OPEN_LAW_API_KEY=your_open_law_api_key

# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key
```

### **Database Migration**
```bash
# Run database migrations to create new tables
alembic upgrade head
```

### **API Rate Limits**
- **CanLII**: 1000 requests per day (free tier)
- **BAILII**: No official rate limits (respectful scraping)
- **Google Gemini**: 15 requests per minute (free tier)

## 📊 **Performance Considerations**

### **Caching Strategy**
- **Local Database**: Cache frequently accessed legal data
- **Session Persistence**: Store chat sessions in database
- **Search Results**: Cache search results for faster retrieval

### **Search Optimization**
- **Relevance Scoring**: AI-powered relevance ranking
- **Result Limiting**: Configurable result limits
- **Pagination**: Support for large result sets
- **Filtering**: Jurisdiction and date filtering

### **Response Time**
- **Legal Database Search**: 2-5 seconds
- **Hybrid Search**: 5-10 seconds
- **Chat Response**: 1-3 seconds
- **Document Analysis**: 10-30 seconds

## 🔒 **Security & Privacy**

### **Data Protection**
- **User Isolation**: Each user's data is isolated
- **Session Privacy**: Chat sessions are user-specific
- **API Security**: Secure API key management
- **Data Encryption**: Sensitive data encrypted at rest

### **Legal Compliance**
- **Terms of Service**: Compliance with legal database terms
- **Rate Limiting**: Respectful API usage
- **Data Attribution**: Proper source attribution
- **Copyright Respect**: Respect for legal content copyrights

## 🚀 **Getting Started**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Set Environment Variables**
```bash
export CANLII_API_KEY="your_api_key"
export GOOGLE_API_KEY="your_gemini_key"
```

### **3. Run Database Migrations**
```bash
alembic upgrade head
```

### **4. Start the Application**
```bash
# Backend
uvicorn backend.app.main:app --reload

# Frontend
cd frontend && npm run dev
```

### **5. Access Chat Interface**
Navigate to `/chat` to start using the legal chat system.

## 🔮 **Future Enhancements**

### **Planned Features**
1. **Advanced Legal Search**: Boolean search operators
2. **Citation Network**: Visual citation relationships
3. **Legal Alerts**: Notifications for new relevant cases
4. **Export Functionality**: Export chat sessions and research
5. **Collaboration**: Shared chat sessions and research

### **Additional Legal Databases**
1. **PACER**: US federal court records
2. **Justia**: US case law and legal information
3. **FindLaw**: Comprehensive legal database
4. **Legal Information Institute**: Cornell Law School

### **AI Enhancements**
1. **Legal Citation Generation**: Automatic citation formatting
2. **Case Brief Generation**: AI-generated case summaries
3. **Legal Writing Assistant**: Help with legal document drafting
4. **Precedent Analysis**: Deep analysis of legal precedents

## 📞 **Support**

For technical support or feature requests:
1. Check the troubleshooting section
2. Review API documentation
3. Check server logs for detailed error messages
4. Contact the development team with specific issues

---

This legal database integration transforms Law-GPT into a comprehensive legal research platform, providing users with access to vast legal knowledge and persistent conversation capabilities for complex legal research tasks.
