from sentence_transformers import SentenceTransformer

# Load the embedding model once (downloads automatically the first time)
model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_chunks(chunks):
    embeddings = model.encode(chunks)
    return embeddings

if __name__ == "__main__":
    from src.extract import extract_text_from_pdf
    from src.chunk import chunk_text

    text = extract_text_from_pdf("sample.pdf")
    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks)

    print(f"Number of chunks: {len(chunks)}")
    print(f"Shape of embeddings: {embeddings.shape}")
    print(f"First embedding (first 10 numbers):\n{embeddings[0][:10]}")