#!/usr/bin/env python3
"""Test script to verify OpenAI LLM integration."""

import asyncio
import os
from dotenv import load_dotenv
from solver_verifier.models.agent_config import SystemSettings
from solver_verifier.services.llm_service import LLMService

# Load environment variables
load_dotenv()

async def test_llm_connection():
    """Test basic LLM connection and functionality."""
    
    # Initialize settings
    settings = SystemSettings()
    
    print(f"OpenAI API Key configured: {'Yes' if settings.openai_api_key else 'No'}")
    print(f"OpenAI Model: {settings.openai_model}")
    print(f"OpenAI Temperature: {settings.openai_temperature}")
    print(f"OpenAI Max Tokens: {settings.openai_max_tokens}")
    print()
    
    # Initialize LLM service
    llm_service = LLMService(settings)
    
    print(f"LLM Service configured: {'Yes' if llm_service.is_configured() else 'No'}")
    print()
    
    if not llm_service.is_configured():
        print("⚠️  LLM service is not configured. Please set OPENAI_API_KEY in .env file")
        return False
    
    try:
        # Test basic connection
        print("🔄 Testing OpenAI connection...")
        connection_ok = await llm_service.test_connection()
        
        if connection_ok:
            print("✅ OpenAI connection successful!")
        else:
            print("❌ OpenAI connection failed!")
            return False
        
        # Test JSON response
        print("\n🔄 Testing JSON response...")
        json_response = await llm_service.call_llm_json(
            system_prompt="You are a helpful assistant that responds in JSON format.",
            user_prompt="Respond with a simple JSON object containing a 'message' field with 'Hello World' as the value.",
            temperature=0.1
        )
        
        print(f"✅ JSON Response: {json_response}")
        
        if 'message' in json_response and json_response['message'] == 'Hello World':
            print("✅ JSON parsing works correctly!")
            return True
        else:
            print("⚠️  JSON response format unexpected")
            return False
            
    except Exception as e:
        print(f"❌ LLM test failed: {str(e)}")
        return False

async def main():
    """Main test function."""
    print("=== OpenAI LLM Integration Test ===")
    print()
    
    success = await test_llm_connection()
    
    print()
    if success:
        print("🎉 All LLM tests passed! The system is ready to use.")
    else:
        print("⚠️  LLM tests failed. Please check your OpenAI API key configuration.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())