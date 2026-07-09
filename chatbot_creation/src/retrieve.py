import psycopg2
from embed import model  # reuse the same loaded model

conn = psycopg2.connect(
    host="localhost",
    dbname="AdventureWorks",
    user="postgres",        
    password="5594"
)
cur = conn.cursor()

def retrieve_relevant_chunks(question, top_k=3):
    # Step 1: embed the question the same way we embedded the chunks
    question_embedding = model.encode(question).tolist()

    # Step 2: find the closest chunks using pgvector's cosine distance operator
    cur.execute(
        """
        SELECT chunk_text, embedding <=> %s::vector AS distance
        FROM document_chunks
        ORDER BY distance ASC
        LIMIT %s
        """,
        (question_embedding, top_k)
    )

    results = cur.fetchall()
    return results

if __name__ == "__main__":
    question = "where do the kandy is located?"
    results = retrieve_relevant_chunks(question)

    for i, (chunk_text, distance) in enumerate(results):
        print(f"\n--- Match {i+1} (distance: {distance:.4f}) ---")
        print(chunk_text)