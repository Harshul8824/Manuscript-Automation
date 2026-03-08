import sys
from pathlib import Path

sys.path.append(str(Path(".").resolve()))

from services.parser import DocumentParser

parser = DocumentParser("tmp/raw_test_manuscript_DR_study.docx")
paras = parser._extract_paragraphs()

for i, p in enumerate(paras[:20]):
    print(f"[{i}] {p['role']:15} | Size: {p.get('ooxml_properties', {}).get('size_pt')} | Bold: {p.get('ooxml_properties', {}).get('bold')} | Align: {p.get('ooxml_properties', {}).get('alignment')} | Text: {repr(p['text'][:80])}")

print("\nTitle extracted:", parser._find_title(paras))
print("Authors extracted:", parser._find_authors(paras))
print("\nIs Author List Match on para 0:", parser._looks_like_author_list(paras[0]['text']))
print("Is Author List Match on para 1:", parser._looks_like_author_list(paras[1]['text']))
