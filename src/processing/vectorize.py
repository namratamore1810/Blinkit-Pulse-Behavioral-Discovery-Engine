import json
import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# We use all-MiniLM-L6-v2 because it is free, fast, and highly effective for semantic search
MODEL_NAME = 'all-MiniLM-L6-v2'
INDEX_NAME = 'blinkit-pulse'

def vectorize_and_upload(filepath):
    api_key = os.getenv('PINECONE_API_KEY')
    if not api_key:
        print("Error: PINECONE_API_KEY is not set in .env")
        return
        
    print("Initializing Pinecone client...")
    pc = Pinecone(api_key=api_key)
    
    # Check if index exists, create if not (using default dimensions for MiniLM which is 384)
    if INDEX_NAME not in pc.list_indexes().names():
        print(f"Creating Pinecone index '{INDEX_NAME}' (Dimensions: 384)...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1' # Default free tier region
            )
        )
        
    index = pc.Index(INDEX_NAME)
    
    print(f"Loading local embedding model ({MODEL_NAME})...")
    model = SentenceTransformer(MODEL_NAME)
    
    print(f"Loading processed chunks from {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
        
    print(f"Starting vectorization for {len(chunks)} chunks...")
    
    # Process in batches to avoid overwhelming memory or the Pinecone API
    batch_size = 100
    import uuid
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        
        texts = [item['text_chunk'] for item in batch]
        # Generate random UUIDs since we removed chunk_id from the JSON to save space
        ids = [uuid.uuid4().hex for _ in batch]
        
        # We need to format the metadata properly (lists must be converted to strings/dicts per Pinecone rules)
        # Pinecone accepts list of strings, so keyword_tags is fine.
        metadatas = []
        for item in batch:
            metadatas.append({
                'rating': item.get('rating') if item.get('rating') is not None else -1,
                'keyword_tags': item.get('keyword_tags', []),
                'text': item.get('text_chunk', '') # Store original text in metadata for RAG retrieval
            })
            
        # Generate embeddings
        embeddings = model.encode(texts).tolist()
        
        # Prepare payload: [(id, embedding, metadata), ...]
        records = zip(ids, embeddings, metadatas)
        
        # Upsert to Pinecone
        index.upsert(vectors=list(records))
        print(f"Upserted batch {i//batch_size + 1} / {(len(chunks)//batch_size) + 1}...")

    print("Successfully uploaded all vectors to Pinecone!")

if __name__ == "__main__":
    # For testing, find the latest processed_feedback file
    processed_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'processed')
    if os.path.exists(processed_dir):
        files = [f for f in os.listdir(processed_dir) if f.startswith('processed_feedback_') and f.endswith('.json')]
        if files:
            latest_file = sorted(files)[-1]
            vectorize_and_upload(os.path.join(processed_dir, latest_file))
        else:
            print("No processed feedback files found in data/processed/")
