import PyPDF2
from pathlib import Path
from typing import List

def extract_pdf_text(pdf_path: Path) -> List[str]:
    pages = []
    print(f"Reading PDF: {pdf_path}")
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            num_pages = len(reader.pages)
            print(f"PDF has {num_pages} pages.")
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    print(f"Page {i+1}: Extracted {len(text)} characters.")
                    pages.append(text)
                else:
                    print(f"Page {i+1}: No text extracted (shadow/image page?)")
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return pages
