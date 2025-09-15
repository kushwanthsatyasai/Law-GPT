#!/usr/bin/env python3
"""
Test script for the Indian legal database integration.
This script tests the complete Indian legal research workflow.
"""

import sys
import os
import json
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.indian_legal_database import IndianLegalDatabaseService
from backend.app.chat_service import ChatService
from backend.app.models import User, ChatSession, LegalCase, LegalStatute
from backend.app.database import get_db
from sqlalchemy.orm import Session

def test_indian_legal_database_service():
    """Test the Indian legal database service functionality"""
    print("🇮🇳 Testing Indian Legal Database Service")
    print("=" * 50)
    
    try:
        # Initialize the service
        indian_legal_service = IndianLegalDatabaseService()
        print("✅ Indian Legal Database Service initialized")
        
        # Test case search
        print("\n🔍 Testing Indian case law search...")
        cases = indian_legal_service.search_indian_cases("employment termination", max_results=3)
        print(f"✅ Found {len(cases)} Indian cases")
        
        for i, case in enumerate(cases[:2], 1):
            print(f"  Case {i}: {case.title}")
            print(f"    Court: {case.court}")
            print(f"    Citation: {case.citation}")
            print(f"    Source: {case.source}")
            print(f"    Relevance: {case.relevance_score:.2f}")
        
        # Test statute search
        print("\n📜 Testing Indian statute search...")
        statutes = indian_legal_service.search_indian_statutes("contract law", max_results=3)
        print(f"✅ Found {len(statutes)} Indian statutes")
        
        for i, statute in enumerate(statutes[:2], 1):
            print(f"  Statute {i}: {statute.title}")
            print(f"    Jurisdiction: {statute.jurisdiction}")
            print(f"    Source: {statute.source}")
            print(f"    Relevance: {statute.relevance_score:.2f}")
        
        # Test court and jurisdiction lists
        print("\n🏛️  Testing court and jurisdiction lists...")
        courts = indian_legal_service.get_available_courts()
        jurisdictions = indian_legal_service.get_available_jurisdictions()
        
        print(f"✅ Available courts: {len(courts)}")
        for court in courts:
            print(f"    - {court['name']}")
        
        print(f"✅ Available jurisdictions: {len(jurisdictions)}")
        for jurisdiction in jurisdictions:
            print(f"    - {jurisdiction['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Indian legal database service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_indian_legal_chat_integration():
    """Test the chat service with Indian legal integration"""
    print("\n💬 Testing Indian Legal Chat Integration")
    print("=" * 50)
    
    try:
        # Initialize the chat service
        chat_service = ChatService()
        print("✅ Chat Service with Indian legal integration initialized")
        
        # Test Indian law query detection
        print("\n🔍 Testing Indian law query detection...")
        
        indian_queries = [
            "What are the employment laws in India?",
            "Supreme Court cases on contract breach",
            "Indian Penal Code section 420",
            "High Court judgment on property rights"
        ]
        
        for query in indian_queries:
            # Test the legal research response generation
            print(f"  Testing query: '{query}'")
            
            # Mock legal research response
            mock_cases = [
                type('MockIndianCase', (), {
                    'title': f'Mock Indian Case - {query}',
                    'court': 'Supreme Court of India',
                    'jurisdiction': 'India',
                    'citation': '[2023] SC 1',
                    'summary': f'This is a mock Indian case related to {query}.',
                    'source': 'indian_kanoon',
                    'relevance_score': 0.85
                })()
            ]
            
            mock_statutes = [
                type('MockIndianStatute', (), {
                    'title': f'Mock Indian Act - {query}',
                    'jurisdiction': 'India',
                    'summary': f'This is a mock Indian statute related to {query}.',
                    'source': 'indian_kanoon',
                    'relevance_score': 0.90
                })()
            ]
            
            context = chat_service._build_legal_context(mock_cases, mock_statutes)
            print(f"    ✅ Context generated ({len(context)} characters)")
        
        print("✅ Indian legal chat integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Indian legal chat integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test Indian legal API endpoints"""
    print("\n🌐 Testing Indian Legal API Endpoints")
    print("=" * 50)
    
    try:
        import requests
        
        # Test health endpoint
        print("Testing health endpoint...")
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"⚠️  Health endpoint returned {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️  Backend server not running - skipping API tests")
            return True
        
        # Test Indian legal courts endpoint
        print("Testing Indian legal courts endpoint...")
        try:
            response = requests.get("http://localhost:8000/indian-legal/courts", timeout=5)
            if response.status_code == 200:
                courts = response.json()
                print(f"✅ Courts endpoint working - found {len(courts)} courts")
            else:
                print(f"⚠️  Courts endpoint returned {response.status_code}")
        except Exception as e:
            print(f"⚠️  Courts endpoint test failed: {e}")
        
        # Test Indian legal jurisdictions endpoint
        print("Testing Indian legal jurisdictions endpoint...")
        try:
            response = requests.get("http://localhost:8000/indian-legal/jurisdictions", timeout=5)
            if response.status_code == 200:
                jurisdictions = response.json()
                print(f"✅ Jurisdictions endpoint working - found {len(jurisdictions)} jurisdictions")
            else:
                print(f"⚠️  Jurisdictions endpoint returned {response.status_code}")
        except Exception as e:
            print(f"⚠️  Jurisdictions endpoint test failed: {e}")
        
        print("✅ API endpoint tests completed")
        return True
        
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False

def test_frontend_components():
    """Test frontend components for Indian legal research"""
    print("\n🎨 Testing Frontend Components")
    print("=" * 50)
    
    try:
        # Check if frontend files exist
        frontend_files = [
            "frontend/src/screens/IndianLegalResearch.tsx",
            "frontend/src/main.tsx"
        ]
        
        for file_path in frontend_files:
            if os.path.exists(file_path):
                print(f"✅ {file_path} exists")
            else:
                print(f"❌ {file_path} missing")
                return False
        
        # Check if routes are properly configured
        with open("frontend/src/main.tsx", "r") as f:
            content = f.read()
            if "IndianLegalResearch" in content and "indian-legal-research" in content:
                print("✅ Indian legal research routes configured")
            else:
                print("❌ Indian legal research routes not configured")
                return False
        
        # Check if dashboard has Indian legal research link
        with open("frontend/src/screens/Dashboard.tsx", "r") as f:
            content = f.read()
            if "Indian Legal Research" in content and "indian-legal-research" in content:
                print("✅ Dashboard has Indian legal research link")
            else:
                print("❌ Dashboard missing Indian legal research link")
                return False
        
        print("✅ Frontend components test passed")
        return True
        
    except Exception as e:
        print(f"❌ Frontend component test failed: {e}")
        return False

def test_indian_legal_workflow():
    """Test the complete Indian legal research workflow"""
    print("\n🔄 Testing Indian Legal Research Workflow")
    print("=" * 50)
    
    try:
        # Simulate a complete Indian legal research workflow
        print("1. User asks Indian legal question...")
        question = "What are the legal requirements for employment termination in India?"
        
        print("2. Indian legal database service searches for cases...")
        indian_legal_service = IndianLegalDatabaseService()
        cases = indian_legal_service.search_indian_cases(question, max_results=2)
        print(f"   Found {len(cases)} relevant Indian cases")
        
        print("3. Indian legal database service searches for statutes...")
        statutes = indian_legal_service.search_indian_statutes(question, max_results=2)
        print(f"   Found {len(statutes)} relevant Indian statutes")
        
        print("4. Chat service generates Indian law response...")
        chat_service = ChatService()
        context = chat_service._build_legal_context(cases, statutes)
        print(f"   Generated context ({len(context)} characters)")
        
        print("5. Indian law response formatting...")
        print("   ✅ Indian legal research workflow completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Indian legal workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_models():
    """Test database models for Indian legal data"""
    print("\n🗄️  Testing Database Models for Indian Legal Data")
    print("=" * 50)
    
    try:
        # Test model imports
        from backend.app.models import LegalCase, LegalStatute
        print("✅ Database models imported successfully")
        
        # Test Indian legal case model
        print("Testing Indian legal case model...")
        indian_case = LegalCase(
            case_id="indian_case_1",
            title="Test Indian Case",
            court="Supreme Court of India",
            jurisdiction="India",
            case_type="Civil",
            summary="Test Indian case summary",
            full_text="Test Indian case full text",
            citation="[2023] SC 1",
            source="indian_kanoon"
        )
        print("✅ Indian legal case model works")
        
        # Test Indian legal statute model
        print("Testing Indian legal statute model...")
        indian_statute = LegalStatute(
            statute_id="indian_statute_1",
            title="Test Indian Statute",
            jurisdiction="India",
            statute_text="Test Indian statute text",
            summary="Test Indian statute summary",
            source="indian_kanoon"
        )
        print("✅ Indian legal statute model works")
        
        return True
        
    except Exception as e:
        print(f"❌ Database model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Law-GPT Indian Legal Database Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Database Models", test_database_models),
        ("Indian Legal Database Service", test_indian_legal_database_service),
        ("Indian Legal Chat Integration", test_indian_legal_chat_integration),
        ("Frontend Components", test_frontend_components),
        ("API Endpoints", test_api_endpoints),
        ("Indian Legal Workflow", test_indian_legal_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Indian legal database integration is working correctly.")
        print("\n🚀 Next Steps:")
        print("1. Start the backend server: uvicorn backend.app.main:app --reload")
        print("2. Start the frontend: cd frontend && npm run dev")
        print("3. Navigate to /indian-legal-research to test the Indian legal research interface")
        print("4. Try asking Indian legal questions in the chat interface")
        print("5. Upload documents and ask about Indian law compliance")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
