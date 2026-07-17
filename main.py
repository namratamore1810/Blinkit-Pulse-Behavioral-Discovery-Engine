import argparse
import sys
import json
import re
from src.rag.retriever import SemanticRetriever
from src.rag.generator import InsightGenerator

def run_pipeline(question: str, top_k: int = 15):
    print("="*50)
    print("BLINKIT PULSE: BEHAVIORAL DISCOVERY ENGINE")
    print("="*50)
    print(f"\nAnalyzing Question: {question}\n")
    
    try:
        # Step 1: Retrieve context
        retriever = SemanticRetriever()
        contexts = retriever.search(query=question, top_k=top_k)
        
        if not contexts:
            print("No relevant context found in the database.")
            return
            
        print(f"\nFound {len(contexts)} highly relevant reviews/comments.")
        
        # Step 2: Generate Insight
        generator = InsightGenerator()
        analysis_raw = generator.generate_insight(question=question, retrieved_contexts=contexts)
        
        # Parse JSON
        try:
            # Clean up potential markdown blocks if LLM ignores instruction
            clean_json = re.sub(r'```json\n|```\n?', '', analysis_raw).strip()
            data = json.loads(clean_json)
            
            print("\n" + "="*50)
            print("AI BEHAVIORAL ANALYSIS (VALIDATED)")
            print("="*50)
            
            if "error" in data:
                print(f"Result: {data['error']}")
            else:
                for idx, insight in enumerate(data.get('insights', [])):
                    print(f"\n{idx+1}. {insight['theme']} (Confidence: {insight['confidence_score']})")
                    print(f"   Description: {insight['description']}")
                    print(f"   Sources Corroborated: {insight['corroborating_sources']}")
                    
                print("\nACTIONABLE RECOMMENDATIONS:")
                for rec in data.get('actionable_recommendations', []):
                    print(f"- {rec}")
                    
        except json.JSONDecodeError:
            print("\n" + "="*50)
            print("AI BEHAVIORAL ANALYSIS (RAW - PARSE FAILED)")
            print("="*50)
            print(analysis_raw)
            
        print("\n" + "="*50 + "\n")
        
    except Exception as e:
        print(f"\nError running pipeline: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Blinkit Pulse Discovery Engine.')
    parser.add_argument('--question', type=str, required=True, help='The business question you want to ask the engine.')
    parser.add_argument('--k', type=int, default=15, help='Number of context chunks to retrieve (default: 15).')
    
    args = parser.parse_args()
    
    run_pipeline(args.question, args.k)
