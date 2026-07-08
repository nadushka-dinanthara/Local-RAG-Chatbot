import pdfplumber

def extract_text_from_pdf(pdf_path):
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_text

if __name__ == "__main__":
    text = extract_text_from_pdf("sample.pdf")
    print(f"Extracted {len(text)} characters")
    print(text[:500])