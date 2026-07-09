from src.retrieve import retrieve_relevant_chunks
from rerank import rerank_chunks
import requests

def generate_answer(question, top_k=3):
    # Stage 1: cast a wider net (e.g. top 10 candidates)
    candidates = retrieve_relevant_chunks(question, top_k=10)

    # Stage 2: rerank and narrow down to the best top_k
    top_chunks = rerank_chunks(question, candidates, top_k=top_k)

    context = "\n\n".join(top_chunks)
    
    prompt = f"""Answer the question using only the context below. If the context doesn't contain the answer, say so.

Context:
{context}

Question: {question}

Answer:"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]