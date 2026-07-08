import os
import psycopg2
from src.extract import extract_text_from_pdf
from src.chunk import chunk_text
from src.embed import embed_chunks

conn = psycopg2.connect(
    host="localhost",
    dbname="AdventureWorks",
    user="postgres",
    password="5594")
cur = conn.cursor()


def is_already_processed(filename):
    cur.execute(
        "SELECT 1 FROM document_chunks WHERE source_file = %s LIMIT 1", (filename,))
    return cur.fetchone() is not None


def store_chunks(pdf_path, filename):
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks)

    for chunk, embedding in zip(chunks, embeddings):
        embedding_list = embedding.tolist()
        cur.execute(
            "INSERT INTO document_chunks (chunk_text, embedding, source_file) VALUES (%s, %s, %s)",
            (chunk, embedding_list, filename)
        )

    conn.commit()
    print(f"Inserted {len(chunks)} chunks from {filename}")


def store_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            if is_already_processed(filename):
                print(f"Skipping {filename} — already in database")
                continue
            full_path = os.path.join(folder_path, filename)
            store_chunks(full_path, filename)


if __name__ == "__main__":
    store_folder("pdfs")
    cur.close()
    conn.close()
