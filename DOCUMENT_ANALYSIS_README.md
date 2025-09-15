# Document Analysis Feature

## Overview

The Law-GPT application now includes a comprehensive document analysis feature that uses OCR and AI to analyze legal documents, identify clauses, and assess their safety levels. This feature is particularly useful for:

- **Agreement Analysis**: Review contracts, NDAs, employment agreements, etc.
- **Form Analysis**: Analyze bank application forms, legal forms, etc.
- **Risk Assessment**: Identify potentially problematic clauses
- **Safety Recommendations**: Get AI-powered suggestions for improvement

## Features

### 🔍 **Advanced OCR Processing**
- **Multi-engine OCR**: Uses PDFMiner, PyMuPDF, and EasyOCR for maximum text extraction accuracy
- **PDF Support**: Handles both text-based and scanned PDFs
- **Image Support**: Processes PNG, JPG, JPEG images
- **Fallback Processing**: Multiple extraction methods ensure maximum text recovery

### 🤖 **AI-Powered Clause Analysis**
- **Clause Identification**: Automatically identifies 8+ types of legal clauses:
  - Termination clauses
  - Payment terms
  - Liability and indemnification
  - Confidentiality agreements
  - Intellectual property rights
  - Governing law and jurisdiction
  - Force majeure clauses
  - Warranties and representations

### 🎨 **Color-Coded Safety Assessment**
- **🟢 Safe Clauses**: Fair and reasonable terms (Green)
- **🟡 Warning Clauses**: Potentially problematic terms (Yellow)
- **🔴 Dangerous Clauses**: High-risk terms requiring immediate attention (Red)

### 📊 **Comprehensive Analysis Dashboard**
- **Risk Assessment**: Overall document risk level (Low/Medium/High)
- **Statistics**: Count of safe, warning, and dangerous clauses
- **Detailed Explanations**: AI-generated explanations for each clause
- **Recommendations**: Specific suggestions for improvement
- **Processing Time**: Track analysis performance

## How It Works

### 1. **Document Upload**
- Users upload documents through the existing upload interface
- System automatically offers analysis after successful upload
- Supports PDF, PNG, JPG, JPEG formats

### 2. **Text Extraction**
- **PDFMiner**: Extracts text from text-based PDFs
- **PyMuPDF**: Handles complex layouts and scanned PDFs
- **EasyOCR**: Processes image-based content with high accuracy
- **Fallback Chain**: Multiple methods ensure maximum text recovery

### 3. **Clause Identification**
- Uses regex patterns to identify legal clauses
- Focuses on specific areas based on user preferences
- Extracts context around identified clauses

### 4. **AI Analysis**
- Each clause is analyzed using Google Gemini AI
- Considers fairness, enforceability, and industry best practices
- Generates safety assessments and recommendations

### 5. **Results Display**
- Color-coded interface shows safety levels
- Detailed explanations for each clause
- Overall risk assessment
- Actionable recommendations

## API Endpoints

### `POST /analyze-document`
Analyzes a document for legal clauses and safety assessment.

**Request Body:**
```json
{
  "document_id": 123,
  "analysis_type": "comprehensive", // "comprehensive", "quick", "specific"
  "focus_areas": ["payment", "termination", "liability"] // Optional
}
```

**Response:**
```json
{
  "document_id": 123,
  "document_title": "Employment Agreement",
  "analysis_status": "completed",
  "total_clauses": 15,
  "safe_clauses": 8,
  "warning_clauses": 5,
  "dangerous_clauses": 2,
  "clauses": [
    {
      "clause_text": "The employee may be terminated at will...",
      "clause_type": "termination",
      "safety_level": "dangerous",
      "explanation": "This clause heavily favors the employer...",
      "recommendations": "Consider adding notice periods and cause requirements..."
    }
  ],
  "summary": "Document Analysis Summary...",
  "overall_risk_level": "medium",
  "processing_time": 12.5
}
```

### `GET /documents`
Retrieves all documents for the current user.

## Frontend Components

### DocumentAnalysis.tsx
- Main analysis interface with color-coded results
- Configurable analysis settings
- Real-time processing status
- Detailed clause breakdown

### Enhanced Upload Flow
- Automatic analysis prompt after upload
- Seamless navigation to analysis results

### Enhanced Dashboard
- Document list with analysis buttons
- Real-time document loading
- Quick access to analysis features

## Installation & Setup

### Backend Dependencies
The following packages have been added to `requirements.txt`:
```
opencv-python==4.10.0.84
easyocr==1.7.2
pymupdf==1.24.3
```

### Installation Steps
1. Install new dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. For EasyOCR, you may need additional system dependencies:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install libgl1-mesa-glx libglib2.0-0
   
   # macOS
   brew install libgl
   ```

3. Restart the backend service:
   ```bash
   uvicorn backend.app.main:app --reload
   ```

## Usage Examples

### 1. **Contract Analysis**
Upload a service agreement and get analysis of:
- Payment terms and schedules
- Termination conditions
- Liability limitations
- Confidentiality requirements

### 2. **Employment Agreement Review**
Analyze employment contracts for:
- At-will employment clauses
- Non-compete restrictions
- Intellectual property assignments
- Severance terms

### 3. **Bank Application Forms**
Review financial documents for:
- Hidden fees and charges
- Unfair terms and conditions
- Liability limitations
- Dispute resolution procedures

## Configuration

### Analysis Types
- **Comprehensive**: Analyzes all clause types (default)
- **Quick**: Focuses on high-priority clauses only
- **Specific**: Analyzes only selected focus areas

### Focus Areas
Users can select specific areas to focus on:
- `termination` - Employment termination clauses
- `payment` - Payment terms and billing
- `liability` - Liability and indemnification
- `confidentiality` - Non-disclosure agreements
- `intellectual_property` - IP rights and assignments
- `governing_law` - Jurisdiction and dispute resolution
- `force_majeure` - Force majeure and act of god clauses
- `warranty` - Warranties and representations

## Performance Considerations

### Processing Time
- **Small documents** (< 5 pages): 5-15 seconds
- **Medium documents** (5-20 pages): 15-45 seconds
- **Large documents** (> 20 pages): 45+ seconds

### Optimization Tips
1. Use "Quick" analysis for initial screening
2. Focus on specific areas for targeted analysis
3. Process documents during off-peak hours
4. Consider document size when uploading

## Error Handling

The system includes comprehensive error handling:
- **OCR Failures**: Automatic fallback to alternative methods
- **AI Analysis Errors**: Graceful degradation with manual review prompts
- **Network Issues**: Retry mechanisms and user notifications
- **Invalid Documents**: Clear error messages and guidance

## Security & Privacy

- All document processing happens server-side
- Documents are stored securely in user-specific directories
- AI analysis is performed using Google Gemini API
- No document content is logged or stored permanently
- Analysis results are user-specific and not shared

## Future Enhancements

### Planned Features
1. **Batch Analysis**: Process multiple documents simultaneously
2. **Comparison Mode**: Compare two documents side-by-side
3. **Template Matching**: Match clauses against standard templates
4. **Export Reports**: Generate PDF reports of analysis results
5. **Integration**: Connect with popular document management systems

### Advanced Analysis
1. **Sentiment Analysis**: Assess the tone and fairness of language
2. **Legal Precedent**: Reference similar cases and rulings
3. **Compliance Checking**: Verify against regulatory requirements
4. **Negotiation Suggestions**: AI-powered negotiation strategies

## Troubleshooting

### Common Issues

**1. OCR Not Working**
- Ensure all dependencies are installed
- Check document quality and resolution
- Try different analysis types

**2. Slow Processing**
- Use "Quick" analysis for initial screening
- Focus on specific areas instead of comprehensive analysis
- Check server resources and memory usage

**3. Analysis Errors**
- Verify document contains readable text
- Try re-uploading the document
- Check API key configuration

**4. Missing Clauses**
- Try different focus areas
- Use comprehensive analysis mode
- Check if document is image-based (may need better OCR)

## Support

For technical support or feature requests:
1. Check the troubleshooting section above
2. Review the API documentation
3. Check server logs for detailed error messages
4. Contact the development team with specific error details

---

This document analysis feature transforms Law-GPT into a comprehensive legal document review platform, making it easier for users to understand and assess the safety of their legal documents.
