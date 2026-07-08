import requests
from src.retrieve import retrieve_relevant_chunks

def generate_answer(question, top_k=3):
    # Step 1: get relevant chunks
    results = retrieve_relevant_chunks(question, top_k)
    context = "\n\n".join([chunk_text for chunk_text, distance in results])

    # Step 2: build the prompt
    prompt = f"""Answer the question using only the context below. If the context doesn't contain the answer, say so.

Context:
{context}

Question: {question}

Answer:"""

    # Step 3: send to Ollama's local API
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]

if __name__ == "__main__":
    question = "IS Sigiriya is a UNESCO World Heritage Site in Sri Lanka?"
    answer = generate_answer(question)
    print("Answer:\n", answer)