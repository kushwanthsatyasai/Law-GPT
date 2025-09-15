# Indian Legal Database Integration

## Overview

The Law-GPT application now includes comprehensive integration with Indian legal databases, providing access to Indian case law, statutes, and legal precedents. This integration enables users to:

- **Search Indian Case Law**: Access Supreme Court, High Court, and District Court decisions
- **Research Indian Statutes**: Find relevant Indian legislation and regulations
- **Legal Precedent Analysis**: Analyze Indian legal precedents and their implications
- **Context-Aware Responses**: AI responses that understand Indian legal system
- **Hybrid Legal Research**: Combine Indian legal databases with user documents

## 🏛️ **Supported Indian Legal Databases**

### **1. Indian Kanoon API**
- **Coverage**: Comprehensive Indian case law and legislation
- **API Access**: RESTful API with search capabilities
- **Pricing**: Pay-per-use model (₹0.50 per search, ₹0.20 per document)
- **Features**: Advanced search filters, court-specific searches, citation tracking

### **2. SCC Online REST API**
- **Coverage**: Supreme Court and High Court judgments
- **API Access**: RESTful API for legal research
- **Features**: Tribunal decisions, statutory materials, international resources

### **3. Kanoon.dev API**
- **Coverage**: Indian legal information and court data
- **API Access**: API key-based authentication
- **Features**: Court information, case details, legal documents

### **4. Local Database Cache**
- **Purpose**: Store frequently accessed Indian legal data
- **Benefits**: Faster searches, offline access, reduced API costs
- **Storage**: PostgreSQL with full-text search capabilities

## 🔍 **Search Capabilities**

### **Case Law Search**
- **Court Filtering**: Supreme Court, High Court, District Court
- **Date Range**: Filter by case date
- **Case Type**: Civil, Criminal, Constitutional, etc.
- **Relevance Scoring**: AI-powered relevance ranking
- **Citation Information**: Full legal citations and court details

### **Statute Search**
- **Jurisdiction Filtering**: Central, State, Union Territory
- **Act Categories**: Contract, Criminal, Civil, Constitutional, etc.
- **Section Search**: Search specific sections of acts
- **Effective Date**: Filter by enactment date

### **Advanced Search Features**
- **Boolean Operators**: AND, OR, NOT search capabilities
- **Phrase Search**: Exact phrase matching
- **Wildcard Search**: Partial word matching
- **Relevance Ranking**: AI-powered result ranking

## 🤖 **AI-Powered Legal Analysis**

### **Indian Law Context**
- **Legal System Understanding**: Knowledge of Indian legal framework
- **Precedent Analysis**: Analysis of Indian legal precedents
- **Statute Interpretation**: Interpretation of Indian laws
- **Court Hierarchy**: Understanding of Indian court system

### **Response Types**
1. **Case Law Analysis**: Detailed analysis of Indian cases
2. **Statute Interpretation**: Explanation of Indian laws
3. **Legal Precedent Research**: Finding relevant Indian precedents
4. **Hybrid Analysis**: Combining Indian law with user documents

## 🔧 **Technical Implementation**

### **Backend Services**

#### **IndianLegalDatabaseService**
```python
class IndianLegalDatabaseService:
    def search_indian_cases(self, query: str, court: str = "all", max_results: int = 10)
    def search_indian_statutes(self, query: str, jurisdiction: str = "all", max_results: int = 10)
    def search_database_indian_cases(self, db: Session, query: str, max_results: int = 10)
    def search_database_indian_statutes(self, db: Session, query: str, max_results: int = 10)
    def save_indian_legal_data_to_db(self, db: Session, cases: List, statutes: List)
```

#### **Enhanced Chat Service**
- **Indian Law Detection**: Automatically detects Indian law queries
- **Context-Aware Responses**: Different responses for Indian vs international law
- **Source Attribution**: Proper citation of Indian legal sources
- **Jurisdiction Awareness**: Understanding of Indian legal jurisdictions

### **API Endpoints**

#### **Indian Legal Research**
- `POST /indian-legal-research` - Search Indian legal databases
- `GET /indian-legal/courts` - Get available Indian courts
- `GET /indian-legal/jurisdictions` - Get available jurisdictions
- `POST /indian-legal/cases/search` - Search Indian cases specifically
- `POST /indian-legal/statutes/search` - Search Indian statutes specifically

### **Database Schema**

#### **Enhanced Legal Cases Table**
```sql
-- Additional fields for Indian legal cases
ALTER TABLE legal_cases ADD COLUMN jurisdiction VARCHAR(100) DEFAULT 'India';
ALTER TABLE legal_cases ADD COLUMN court VARCHAR(200);
ALTER TABLE legal_cases ADD COLUMN case_type VARCHAR(100);
ALTER TABLE legal_cases ADD COLUMN citation VARCHAR(200);
```

#### **Enhanced Legal Statutes Table**
```sql
-- Additional fields for Indian legal statutes
ALTER TABLE legal_statutes ADD COLUMN jurisdiction VARCHAR(100) DEFAULT 'India';
ALTER TABLE legal_statutes ADD COLUMN section_number VARCHAR(50);
ALTER TABLE legal_statutes ADD COLUMN effective_date TIMESTAMP WITH TIME ZONE;
```

## 🎯 **Usage Examples**

### **1. Indian Case Law Research**
```
Query: "What are the recent Supreme Court cases on employment termination in India?"

Response:
- Searches Indian Kanoon, SCC Online, and Kanoon.dev
- Finds relevant Supreme Court cases
- Provides case summaries and citations
- Explains legal principles under Indian law
- References relevant sections of Indian laws
```

### **2. Indian Statute Research**
```
Query: "What are the legal requirements for contract formation under Indian Contract Act?"

Response:
- Searches Indian legal databases for Contract Act provisions
- Finds relevant sections and amendments
- Provides detailed interpretation
- Explains practical implications
- References case law interpreting the Act
```

### **3. Hybrid Legal Research**
```
Query: "How does this employment contract compare to Indian labor laws?"

Response:
- Analyzes uploaded employment contract
- Searches Indian labor law databases
- Compares contract terms with Indian legal requirements
- Identifies potential compliance issues
- Provides recommendations for Indian law compliance
```

## 📱 **Frontend Features**

### **Indian Legal Research Interface**
- **Search Form**: Advanced search with filters
- **Court Selection**: Dropdown for Indian courts
- **Jurisdiction Filtering**: Central, State, Union Territory
- **Search Type**: Cases, Statutes, or Both
- **Results Display**: Organized by relevance and source

### **Enhanced Chat Interface**
- **Indian Law Detection**: Automatic detection of Indian law queries
- **Source Attribution**: Clear indication of Indian legal sources
- **Citation Formatting**: Proper Indian legal citation format
- **Context Awareness**: Understanding of Indian legal system

### **Dashboard Integration**
- **Indian Legal Research Link**: Quick access to Indian legal research
- **Recent Searches**: Display recent Indian legal searches
- **Search History**: Track Indian legal research history

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Indian Legal Database API Keys
INDIAN_KANOON_API_KEY=your_indian_kanoon_api_key
SCC_ONLINE_API_KEY=your_scc_online_api_key
KANOON_DEV_API_KEY=your_kanoon_dev_api_key

# Google Gemini API (for AI responses)
GOOGLE_API_KEY=your_gemini_api_key
```

### **API Rate Limits**
- **Indian Kanoon**: 1000 requests per day (free tier)
- **SCC Online**: Varies by subscription plan
- **Kanoon.dev**: Varies by API key type
- **Google Gemini**: 15 requests per minute (free tier)

## 💰 **Pricing Information**

### **Indian Kanoon API Pricing**
- **Search**: ₹0.50 per request
- **Document**: ₹0.20 per request
- **Document Fragment**: ₹0.05 per request
- **New Users**: ₹500 free credits for development
- **Non-commercial**: Up to ₹10,000 monthly credits

### **Cost Optimization**
- **Local Caching**: Store frequently accessed data locally
- **Smart Search**: Use relevance scoring to limit API calls
- **Batch Processing**: Group multiple searches together
- **User Limits**: Implement per-user search limits

## 🚀 **Getting Started**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Set Environment Variables**
```bash
export INDIAN_KANOON_API_KEY="your_api_key"
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

### **5. Access Indian Legal Research**
Navigate to `/indian-legal-research` to start using the Indian legal research system.

## 📊 **Performance Considerations**

### **Search Performance**
- **API Response Time**: 2-5 seconds for Indian Kanoon
- **Local Database**: <1 second for cached results
- **Hybrid Search**: 5-10 seconds for combined results
- **Caching Strategy**: 24-hour cache for frequently accessed data

### **Optimization Strategies**
- **Result Caching**: Cache search results for faster subsequent searches
- **Smart Pagination**: Load results in batches
- **Relevance Filtering**: Pre-filter results by relevance score
- **Database Indexing**: Optimize database queries for Indian legal data

## 🔒 **Security & Compliance**

### **Data Protection**
- **API Key Security**: Secure storage of API keys
- **User Data Isolation**: Each user's searches are isolated
- **Search Privacy**: Search queries are not logged permanently
- **Data Encryption**: Sensitive data encrypted at rest

### **Legal Compliance**
- **Terms of Service**: Compliance with Indian legal database terms
- **Attribution Requirements**: Proper source attribution
- **Copyright Respect**: Respect for legal content copyrights
- **Data Usage**: Appropriate use of legal data

## 🌟 **Key Benefits**

### **Comprehensive Indian Legal Access**
- **Vast Database**: Access to thousands of Indian cases and statutes
- **Real-time Updates**: Latest legal developments
- **Multiple Sources**: Cross-reference from multiple databases
- **Reliable Citations**: Accurate legal citations

### **AI-Powered Analysis**
- **Context Understanding**: AI understands Indian legal system
- **Precedent Analysis**: Analysis of Indian legal precedents
- **Statute Interpretation**: Interpretation of Indian laws
- **Practical Guidance**: Real-world legal advice

### **User-Friendly Interface**
- **Intuitive Search**: Easy-to-use search interface
- **Advanced Filters**: Powerful filtering options
- **Results Organization**: Well-organized search results
- **Mobile Responsive**: Works on all devices

## 🔮 **Future Enhancements**

### **Planned Features**
1. **State-Specific Laws**: Access to state-specific legislation
2. **Legal Notifications**: Alerts for new relevant cases
3. **Citation Network**: Visual citation relationships
4. **Legal Brief Generation**: AI-generated case summaries
5. **Document Comparison**: Compare documents with Indian legal standards

### **Additional Indian Legal Databases**
1. **Manupatra**: Comprehensive Indian legal database
2. **SCC Online**: Enhanced SCC Online integration
3. **LegalCrystal**: Indian legal research platform
4. **Indian Legal Information Institute**: Free legal database

### **AI Enhancements**
1. **Hindi Language Support**: Support for Hindi legal queries
2. **Regional Law Support**: Support for regional legal systems
3. **Legal Translation**: Translate legal documents
4. **Compliance Checking**: Check documents against Indian legal requirements

## 📞 **Support**

For technical support or feature requests:
1. Check the troubleshooting section
2. Review API documentation
3. Check server logs for detailed error messages
4. Contact the development team with specific issues

---

This Indian legal database integration transforms Law-GPT into a comprehensive Indian legal research platform, providing users with access to vast Indian legal knowledge and AI-powered analysis capabilities.
