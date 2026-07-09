from sentence_transformers import CrossEncoder

# Load the cross-encoder model once
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank_chunks(question, chunks_with_scores, top_k=3):
    # chunks_with_scores is a list of (chunk_text, distance) from your existing retrieval
    chunk_texts = [chunk_text for chunk_text, distance in chunks_with_scores]

    # Build pairs: (question, chunk) for each candidate
    pairs = [[question, chunk] for chunk in chunk_texts]

    # Cross-encoder scores each pair directly - higher score = more relevant
    scores = cross_encoder.predict(pairs)

    # Combine chunks with their new scores, then sort by score descending
    reranked = sorted(zip(chunk_texts, scores), key=lambda x: x[1], reverse=True)

    # Return just the top_k chunks (text only, matching what generate.py expects)
    return [chunk for chunk, score in reranked[:top_k]]

if __name__ == "__main__":
    from retrieve import retrieve_relevant_chunks

    question = "How kandy kingdom falls?"

    # Stage 1: get a wider net of candidates (say top 10 instead of top 3)
    candidates = retrieve_relevant_chunks(question, top_k=10)

    # Stage 2: rerank and narrow down to the best 3
    top_chunks = rerank_chunks(question, candidates, top_k=3)

    print("Top reranked chunks:\n")
    for i, chunk in enumerate(top_chunks):
        print(f"--- Rank {i+1} ---")
        print(chunk[:200], "...\n")