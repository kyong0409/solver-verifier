#!/usr/bin/env python3
"""Debug script to test pipeline processing."""

import asyncio
import traceback
from solver_verifier.models.agent_config import SystemSettings
from solver_verifier.services.pipeline_service import PipelineService

async def test_pipeline():
    """Test the pipeline with a simple text document."""
    try:
        print("🔄 Initializing settings...")
        settings = SystemSettings()
        print(f"✅ Settings initialized")
        print(f"   OpenAI API Key configured: {'Yes' if settings.openai_api_key else 'No'}")
        print(f"   Analyzer prompt configured: {'Yes' if settings.analyzer_system_prompt else 'No'}")
        print(f"   Verifier prompt configured: {'Yes' if settings.verifier_system_prompt else 'No'}")
        
        print("\n🔄 Initializing pipeline service...")
        pipeline_service = PipelineService(settings)
        print("✅ Pipeline service initialized")
        
        # Create a simple test document
        print("\n🔄 Creating test document...")
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""
            RFP for E-commerce Platform Development
            
            Requirements:
            1. The system must support user registration and authentication
            2. The platform should provide product catalog management
            3. Order processing functionality is required
            4. Payment integration with multiple providers is needed
            5. The system must be scalable to handle 10,000 concurrent users
            """)
            test_file = f.name
        
        print(f"✅ Test document created: {test_file}")
        
        # Process the document
        print("\n🔄 Processing document through pipeline...")
        result = await pipeline_service.process_rfp_documents(
            document_paths=[test_file],
            set_name="Test RFP",
            set_description="Test document for debugging"
        )
        
        print("✅ Pipeline processing completed!")
        print(f"   Status: {result.status}")
        print(f"   Requirements found: {len(result.business_requirements)}")
        print(f"   Hypotheses: {len(result.hypotheses)}")
        print(f"   Verification issues: {len(result.verification_issues or [])}")
        
        # Clean up
        import os
        os.unlink(test_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {str(e)}")
        print(f"📊 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_pipeline())
    print(f"\n{'🎉 Test passed!' if success else '⚠️  Test failed!'}")