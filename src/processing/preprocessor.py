import json
import os
import re
import uuid
import emoji
from datetime import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Behavioral keywords for intent tagging
KEYWORD_TAGS = {
    'pricing': ['price', 'cost', 'expensive', 'cheap', 'delivery fee', 'surge', 'charge'],
    'ui_ux': ['ui', 'ux', 'app', 'crash', 'button', 'glitch', 'bug', 'screen', 'interface'],
    'delivery': ['delivery', 'late', 'fast', 'rider', 'partner', 'time', 'delay', 'minutes'],
    'search': ['search', 'find', 'navigate', 'category', 'categories', 'explore', 'looking'],
    'quality': ['quality', 'fresh', 'rotten', 'expired', 'bad', 'good', 'package', 'damaged'],
    'customer_support': ['support', 'care', 'refund', 'agent', 'bot', 'help', 'call']
}

def clean_twitter_handles(text):
    """Clean excessive @usernames but keep hashtags."""
    # Removes @username strings
    return re.sub(r'@\w+', '', text).strip()

def tag_intent(text):
    """Tag text based on behavioral keywords."""
    text_lower = text.lower()
    tags = []
    for intent, keywords in KEYWORD_TAGS.items():
        if any(keyword in text_lower for keyword in keywords):
            tags.append(intent)
    return tags

def process_feedback_file(filepath):
    print(f"Loading raw data from {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Initialize Langchain chunker
    # Using 1000 character chunks with 100 character overlap to preserve context
    # This ensures 99% of Google Play reviews remain intact as single chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )

    processed_chunks = []
    skipped_spam = 0

    print(f"Processing {len(data)} items...")
    
    for item in data:
        raw_text = item.get('text', '')
        if not raw_text or not isinstance(raw_text, str):
            continue
            
        # 1. Platform-Specific Parsing
        if item.get('source') == 'Twitter/X':
            raw_text = clean_twitter_handles(raw_text)
            
        # 2. Demojize (Convert 😊 to :smiling_face_with_smiling_eyes:)
        text_demojized = emoji.demojize(raw_text)
        
        # Basic cleanup
        clean_text = re.sub(r'\s+', ' ', text_demojized).strip()
        
        # 3. Intent Pre-Filtering (Tagging)
        tags = tag_intent(clean_text)
        
        # 4. Spam Filtering & Length Adjustments
        # Discard if it's less than 5 words (not meaningful for RAG)
        words = clean_text.split()
        if len(words) < 5:
            skipped_spam += 1
            continue
            
        # 5. Text Chunking & Rich Metadata
        chunks = text_splitter.split_text(clean_text)
        
        for i, chunk in enumerate(chunks):
            processed_chunks.append({
                'rating': item.get('rating'),
                'keyword_tags': tags,
                'text_chunk': chunk
            })

    print(f"Preprocessing complete. Removed {skipped_spam} low-value/spam items.")
    print(f"Generated {len(processed_chunks)} metadata-rich chunks for vectorization.")
    
    # Save the processed chunks
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'processed')
    os.makedirs(output_dir, exist_ok=True)
    
    filename = os.path.basename(filepath).replace('raw_', 'processed_')
    output_path = os.path.join(output_dir, filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_chunks, f, indent=4, ensure_ascii=False)
        
    print(f"Saved processed chunks to {output_path}")
    return output_path

if __name__ == "__main__":
    # For testing, find the latest raw_feedback file
    raw_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'raw')
    if os.path.exists(raw_dir):
        files = [f for f in os.listdir(raw_dir) if f.startswith('raw_feedback_') and f.endswith('.json')]
        if files:
            latest_file = sorted(files)[-1] # Gets the most recent by timestamp in filename
            process_feedback_file(os.path.join(raw_dir, latest_file))
        else:
            print("No raw feedback files found in data/raw/")
