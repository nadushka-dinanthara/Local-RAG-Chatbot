import os
import time
import hashlib
import psycopg2
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.extract import extract_text_from_pdf
from src.chunk import chunk_text
from src.embed import embed_chunks

conn = psycopg2.connect(
    host="localhost",
    dbname="AdventureWorks",
    user="postgres",
    password="5594"
)
cur = conn.cursor()


def get_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()


def is_already_processed(file_hash):
    cur.execute(
        "SELECT 1 FROM document_chunks WHERE file_hash = %s LIMIT 1", (file_hash,))
    return cur.fetchone() is not None


def store_chunks(pdf_path, filename, file_hash):
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks)

    for chunk, embedding in zip(chunks, embeddings):
        embedding_list = embedding.tolist()
        cur.execute(
            "INSERT INTO document_chunks (chunk_text, embedding, source_file, file_hash) VALUES (%s, %s, %s, %s)",
            (chunk, embedding_list, filename, file_hash)
        )

    conn.commit()
    print(f"Inserted {len(chunks)} chunks from {filename}")


def process_pdf(filepath):
    filename = os.path.basename(filepath)
    file_hash = get_file_hash(filepath)

    if is_already_processed(file_hash):
        print(f"Skipping {filename} — already processed (same content)")
        return

    print(f"New document detected: {filename}")
    store_chunks(filepath, filename, file_hash)


class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.lower().endswith(".pdf"):
            # small delay to make sure the file finished writing to disk
            time.sleep(1)
            process_pdf(event.src_path)


def process_existing_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            process_pdf(os.path.join(folder_path, filename))


if __name__ == "__main__":
    folder_to_watch = "pdfs"

    print("Checking existing files first...")
    process_existing_files(folder_to_watch)

    print(f"\nWatching '{folder_to_watch}' for new PDFs... (Ctrl+C to stop)")
    observer = Observer()
    observer.schedule(PDFHandler(), path=folder_to_watch, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
