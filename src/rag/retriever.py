import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = 'all-MiniLM-L6-v2'
INDEX_NAME = 'blinkit-pulse'

class SemanticRetriever:
    def __init__(self):
        print("Initializing Retriever...")
        self.api_key = os.getenv('PINECONE_API_KEY')
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY is not set in .env")
            
        self.pc = Pinecone(api_key=self.api_key)
        self.index = self.pc.Index(INDEX_NAME)
        self.model = SentenceTransformer(MODEL_NAME)
        print("Retriever ready.")

    def search(self, query: str, top_k: int = 15, filter_tag: str = None):
        """
        Converts the query to a vector and retrieves the top_k most similar chunks from Pinecone.
        Optionally filters by keyword_tag.
        """
        print(f"Embedding query: '{query}'")
        query_vector = self.model.encode(query).tolist()
        
        print(f"Searching Pinecone for top {top_k} results...")
        
        query_args = {
            "vector": query_vector,
            "top_k": top_k,
            "include_metadata": True
        }
        
        if filter_tag and filter_tag != "All":
            query_args["filter"] = {"keyword_tags": {"$in": [filter_tag]}}
            
        response = self.index.query(**query_args)
        
        results = []
        for match in response['matches']:
            metadata = match.get('metadata', {})
            # We only kept rating, keyword_tags, and text in the metadata
            results.append({
                'score': match['score'],
                'text': metadata.get('text', ''),
                'rating': metadata.get('rating', -1),
                'tags': metadata.get('keyword_tags', [])
            })
            
        return results
