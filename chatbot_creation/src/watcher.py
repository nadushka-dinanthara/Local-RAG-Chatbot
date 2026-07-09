import os
import time
import hashlib
import psycopg2
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from extract import extract_text_from_pdf
from chunk import chunk_text
from embed import embed_chunks

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
    cur.execute("SELECT 1 FROM document_chunks WHERE file_hash = %s LIMIT 1", (file_hash,))
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

def delete_chunks_by_filename(filename):
    cur.execute("DELETE FROM document_chunks WHERE source_file = %s", (filename,))
    deleted_count = cur.rowcount
    conn.commit()
    print(f"Removed {deleted_count} chunks for deleted/changed file: {filename}")

def process_pdf(filepath):
    filename = os.path.basename(filepath)
    file_hash = get_file_hash(filepath)

    if is_already_processed(file_hash):
        print(f"Skipping {filename} — already processed (same content)")
        return

    print(f"New or changed document detected: {filename}")
    store_chunks(filepath, filename, file_hash)

class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.lower().endswith(".pdf"):
            time.sleep(1)  # let the file finish writing to disk
            process_pdf(event.src_path)

    def on_modified(self, event):
        if event.src_path.lower().endswith(".pdf"):
            time.sleep(1)
            filename = os.path.basename(event.src_path)
            file_hash = get_file_hash(event.src_path)

            if is_already_processed(file_hash):
                print(f"{filename} modified but content unchanged (same hash) — skipping")
                return

            print(f"{filename} content changed — removing old chunks and reprocessing")
            delete_chunks_by_filename(filename)
            store_chunks(event.src_path, filename, file_hash)

    def on_deleted(self, event):
        if event.src_path.lower().endswith(".pdf"):
            filename = os.path.basename(event.src_path)
            print(f"{filename} deleted — removing its chunks from the database")
            delete_chunks_by_filename(filename)

    def on_moved(self, event):
        if event.src_path.lower().endswith(".pdf"):
            old_filename = os.path.basename(event.src_path)
            new_filename = os.path.basename(event.dest_path)
            print(f"{old_filename} renamed/moved to {new_filename}")
            cur.execute(
                "UPDATE document_chunks SET source_file = %s WHERE source_file = %s",
                (new_filename, old_filename)
            )
            conn.commit()

def process_existing_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            process_pdf(os.path.join(folder_path, filename))

if __name__ == "__main__":
    folder_to_watch = "../pdfs"  # adjust path relative to where watcher.py lives

    print("Checking existing files first...")
    process_existing_files(folder_to_watch)

    print(f"\nWatching '{folder_to_watch}' for new, modified, deleted, or moved PDFs... (Ctrl+C to stop)")
    observer = Observer()
    observer.schedule(PDFHandler(), path=folder_to_watch, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()