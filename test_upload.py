#!/usr/bin/env python3
"""Test script to test file upload API endpoint."""

import requests
import tempfile
import os

def test_upload_api():
    """Test the /pipeline/process endpoint with a simple file."""
    
    # Create a simple test file
    test_content = """
    RFP for E-commerce Platform Development
    
    Requirements:
    1. The system must support user registration and authentication
    2. The platform should provide product catalog management
    3. Order processing functionality is required
    """
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        test_file_path = f.name
    
    try:
        # Test the API endpoint
        url = "http://localhost:8000/pipeline/process"
        
        with open(test_file_path, 'rb') as f:
            files = {
                'files': ('test_rfp.txt', f, 'text/plain')
            }
            data = {
                'set_name': 'Test Upload',
                'set_description': 'Testing file upload functionality'
            }
            
            print("🔄 Testing file upload...")
            response = requests.post(url, files=files, data=data, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                print("✅ Upload successful!")
                result = response.json()
                print(f"Result: {result}")
            else:
                print("❌ Upload failed!")
                print(f"Error: {response.text}")
                
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
    
    finally:
        # Clean up
        try:
            os.unlink(test_file_path)
        except:
            pass

if __name__ == "__main__":
    test_upload_api()