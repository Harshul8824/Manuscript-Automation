import sys
import os
from pathlib import Path

# Add backend/services to sys.path
sys.path.append(r"d:\DATA SCIENCE AND ML\Project\ManuscriptMagic.AI\backend\services")

try:
    from parser import DocumentParser
    import re

    doc_path = r"D:\DATA SCIENCE AND ML\Project\ManuscriptMagic.AI\template\test.docx"
    print(f"Checking if doc exists: {os.path.exists(doc_path)}")
    
    parser = DocumentParser(doc_path)
    data = parser.extract_all()

    print(f"Total tables extracted: {len(data.get('tables', []))}")
    for i, table in enumerate(data.get('tables', [])):
        print(f"\nTable {i}:")
        print(f"Caption: {table.get('caption')}")
        print(f"Rows: {len(table.get('rows', []))}")
        for row in table.get('rows', [])[:3]:
            print(f"  {row}")

    if not data.get('tables'):
        print("\nTracing raw paragraphs near potential tables...")
        for p in data.get('raw_paragraphs', []):
            if "TABLE" in p['text'].upper():
                print(f"Role: {p['role']}, Text: {p['text'][:100]}")
except Exception as e:
    import traceback
    traceback.print_exc()
