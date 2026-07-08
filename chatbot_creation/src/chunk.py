def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap  # move forward, but overlap a bit with previous chunk

    return chunks

if __name__ == "__main__":
    from src.extract import extract_text_from_pdf

    text = extract_text_from_pdf("sample.pdf")
    chunks = chunk_text(text)

    print(f"Total chunks: {len(chunks)}")
    print("First chunk:\n", chunks[0])
    print("\nSecond chunk:\n", chunks[1])