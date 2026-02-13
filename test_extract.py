from pathlib import Path
import pdftomd
import sys

pdf = Path("uploaded_files/Credit Card Procedure.pdf")
if not pdf.exists():
    print("File not found")
    sys.exit(1)

pages = pdftomd.extract_pdf_text(pdf)
print(f"Extracted {len(pages)} pages.")
for i, p in enumerate(pages):
    print(f"--- Page {i+1} (first 100 chars) ---")
    print(p[:100])
