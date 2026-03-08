import requests
import os
from pathlib import Path

# Base configuration
BASE_URL = "http://localhost:5000/api/documents"
TEST_FILE = Path(__file__).parent.parent.parent / "template" / "test.docx"

def test_full_flow():
    if not TEST_FILE.exists():
        print(f"❌ Test file not found at {TEST_FILE}")
        return

    print(f"🚀 Starting test flow for {TEST_FILE.name}")
    
    # 1. Upload
    print("\n1️⃣  Uploading document...")
    with open(TEST_FILE, 'rb') as f:
        response = requests.post(f"{BASE_URL}/upload", files={'file': f})
    
    if response.status_code != 201:
        print(f"❌ Upload failed: {response.json()}")
        return
        
    data = response.json()
    job_id = data['job_id']
    print(f"✅ Uploaded. Job ID: {job_id}")

    # 2. Analyze
    print("\n2️⃣  Analyzing document (Stage 1-3)...")
    response = requests.post(f"{BASE_URL}/analyze/{job_id}")
    if response.status_code != 200:
        try:
            print(f"❌ Analysis failed: {response.json()}")
        except Exception:
            print(f"❌ Analysis failed (status {response.status_code}): {response.text[:500]}")
        return
        
    report = response.json()
    print(f"✅ Analysis complete.")
    print(f"   Found {len(report['mapping_report'].get('sections', []))} sections")
    print(f"   Found {len(report['mapping_report'].get('tables', []))} tables")

    # 3. Format
    print("\n3️⃣  Formatting document (Stage 4)...")
    response = requests.post(f"{BASE_URL}/format/{job_id}")
    if response.status_code != 200:
        print(f"❌ Formatting failed: {response.text}")
        return
        
    # The formatted doc is already saved in backend/tmp by the API
    print(f"✅ Formatting successful! The output is stored in backend/tmp/test_formatted.docx")

if __name__ == "__main__":
    test_full_flow()
