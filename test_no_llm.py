#!/usr/bin/env python3
"""Test script to test pipeline without LLM calls."""

import asyncio
import tempfile
import os
from solver_verifier.models.agent_config import SystemSettings
from solver_verifier.services.document_parser import DocumentParserService

async def test_document_parsing_only():
    """Test just the document parsing part."""
    try:
        print("🔄 Testing document parser only...")
        
        # Create test document
        test_content = """
        RFP for E-commerce Platform Development
        
        Requirements:
        1. The system must support user registration and authentication
        2. The platform should provide product catalog management
        3. Order processing functionality is required
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            test_file_path = f.name
        
        print(f"✅ Test file created: {test_file_path}")
        
        # Test document parser
        parser = DocumentParserService()
        documents = await parser.parse_documents([test_file_path])
        
        print("✅ Document parsing successful!")
        print(f"   Documents parsed: {len(documents)}")
        for filename, content in documents.items():
            print(f"   {filename}: {len(content)} characters")
            print(f"   Content preview: {content[:200]}...")
        
        # Clean up
        os.unlink(test_file_path)
        return True
        
    except Exception as e:
        print(f"❌ Document parsing test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_settings_loading():
    """Test settings and prompt loading."""
    try:
        print("🔄 Testing settings loading...")
        
        settings = SystemSettings()
        print("✅ Settings loaded successfully!")
        print(f"   OpenAI API Key configured: {'Yes' if settings.openai_api_key else 'No'}")
        print(f"   Analyzer prompt length: {len(settings.analyzer_system_prompt)}")
        print(f"   Verifier prompt length: {len(settings.verifier_system_prompt)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Settings loading failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("=== Non-LLM Infrastructure Test ===\n")
    
    test1 = await test_settings_loading()
    print()
    test2 = await test_document_parsing_only()
    
    print(f"\n{'🎉 Infrastructure tests passed!' if test1 and test2 else '⚠️  Infrastructure tests failed!'}")
    
    return test1 and test2

if __name__ == "__main__":
    asyncio.run(main())