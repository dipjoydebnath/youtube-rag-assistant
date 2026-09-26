import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

def create_vector_db(transcript_text: str):
    """
    Takes a full video transcript, splits it into smaller chunks,
    and stores them in ChromaDB.
    """
    # 1. Split text into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,       # Max characters per chunk
        chunk_overlap=100     # Overlap to preserve context between boundaries
    )
    chunks = text_splitter.split_text(transcript_text)
    print(f"[*] Total text chunks created: {len(chunks)}")

    # 2. Initialize an in-memory ChromaDB client
    chroma_client = chromadb.Client()
    
    # Reset/Create a collection named 'youtube_transcript'
    collection_name = "youtube_transcript"
    
    # Delete existing collection if it exists to avoid old video data
    try:
        chroma_client.delete_collection(name=collection_name)
    except Exception:
        pass

    collection = chroma_client.create_collection(name=collection_name)

    # 3. Add chunks to ChromaDB (Chroma handles embedding generation automatically)
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.add(
        documents=chunks,
        ids=ids
    )
    
    print("[*] Successfully indexed transcript chunks in ChromaDB!")
    return collection

# Quick manual test connecting ingest.py and vector_store.py
if __name__ == "__main__":
    from ingest import get_youtube_transcript
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print("[*] Fetching transcript...")
    raw_transcript = get_youtube_transcript(test_url)
    
    print("[*] Creating Vector Database...")
    db_collection = create_vector_db(raw_transcript)
    
    # Test querying the database
    query = "What is the singer promising?"
    results = db_collection.query(query_texts=[query], n_results=2)
    
    print("\n--- TOP MATCHING CHUNKS FROM CHROMADB ---")
    for i, doc in enumerate(results['documents'][0]):
        print(f"\n[Chunk {i+1}]: {doc}")