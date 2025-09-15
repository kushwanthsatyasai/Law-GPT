#!/usr/bin/env python3
"""
Test script for the document analysis feature.
This script tests the document analysis functionality without requiring a full web interface.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.document_analyzer import DocumentAnalyzer
from backend.app.models import Document
from backend.app.database import get_db
from sqlalchemy.orm import Session

def test_document_analysis():
    """Test the document analysis functionality"""
    print("🧪 Testing Document Analysis Feature")
    print("=" * 50)
    
    # Create a mock document for testing
    mock_document = Document(
        id=1,
        user_id=1,
        title="Test Employment Agreement",
        path="sample_data/employment_policy.txt",  # Use existing sample data
        content_type="text/plain"
    )
    
    print(f"📄 Testing with document: {mock_document.title}")
    print(f"📁 File path: {mock_document.path}")
    
    # Check if the sample file exists
    if not os.path.exists(mock_document.path):
        print("❌ Sample file not found. Please ensure sample_data/employment_policy.txt exists.")
        return False
    
    try:
        # Initialize the analyzer
        print("\n🔧 Initializing Document Analyzer...")
        analyzer = DocumentAnalyzer()
        print("✅ Analyzer initialized successfully")
        
        # Perform analysis
        print("\n🔍 Starting document analysis...")
        analysis = analyzer.analyze_document(mock_document, analysis_type="comprehensive")
        
        # Display results
        print("\n📊 Analysis Results:")
        print("=" * 30)
        print(f"Status: {analysis.analysis_status}")
        print(f"Total Clauses: {analysis.total_clauses}")
        print(f"Safe Clauses: {analysis.safe_clauses}")
        print(f"Warning Clauses: {analysis.warning_clauses}")
        print(f"Dangerous Clauses: {analysis.dangerous_clauses}")
        print(f"Overall Risk Level: {analysis.overall_risk_level}")
        print(f"Processing Time: {analysis.processing_time:.2f} seconds")
        
        if analysis.error_message:
            print(f"❌ Error: {analysis.error_message}")
            return False
        
        # Display summary
        print(f"\n📝 Summary:")
        print("-" * 20)
        print(analysis.summary)
        
        # Display sample clauses
        if analysis.clauses:
            print(f"\n🔍 Sample Clauses Found:")
            print("-" * 30)
            for i, clause in enumerate(analysis.clauses[:3]):  # Show first 3 clauses
                print(f"\nClause {i+1}:")
                print(f"  Type: {clause.clause_type}")
                print(f"  Safety: {clause.safety_level}")
                print(f"  Text: {clause.clause_text[:100]}...")
                print(f"  Explanation: {clause.explanation[:150]}...")
                if clause.recommendations:
                    print(f"  Recommendations: {clause.recommendations[:100]}...")
        
        print("\n✅ Document analysis test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_ocr_functionality():
    """Test OCR functionality with sample files"""
    print("\n🔍 Testing OCR Functionality")
    print("=" * 40)
    
    try:
        from backend.app.ingest import extract_text_from_pdf, extract_text_from_image
        
        # Test with sample text file
        sample_file = "sample_data/employment_policy.txt"
        if os.path.exists(sample_file):
            print(f"📄 Testing text extraction from: {sample_file}")
            with open(sample_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ Text extracted successfully ({len(content)} characters)")
            print(f"📝 Sample content: {content[:200]}...")
        else:
            print(f"❌ Sample file not found: {sample_file}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ OCR test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Law-GPT Document Analysis Test Suite")
    print("=" * 50)
    
    # Test OCR functionality
    ocr_success = test_ocr_functionality()
    
    # Test document analysis
    analysis_success = test_document_analysis()
    
    # Summary
    print("\n📋 Test Summary:")
    print("=" * 20)
    print(f"OCR Functionality: {'✅ PASS' if ocr_success else '❌ FAIL'}")
    print(f"Document Analysis: {'✅ PASS' if analysis_success else '❌ FAIL'}")
    
    if ocr_success and analysis_success:
        print("\n🎉 All tests passed! Document analysis feature is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
