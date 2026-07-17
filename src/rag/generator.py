import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class InsightGenerator:
    def __init__(self):
        print("Initializing Groq Generator...")
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not set in .env")
            
        self.client = Groq(api_key=self.api_key)
        # Using Llama-3.3-70B for high-quality reasoning
        self.model = "llama-3.3-70b-versatile"

    def generate_insight(self, question: str, retrieved_contexts: list):
        """
        Sends the business question and retrieved contexts to the LLM to generate an insight.
        """
        # Format contexts into a single string for the prompt
        context_str = ""
        for i, ctx in enumerate(retrieved_contexts):
            context_str += f"\n--- Review {i+1} (Rating: {ctx['rating']}) ---\n"
            context_str += f"{ctx['text']}\n"
            
        system_prompt = (
            "You are an expert Consumer Behavior Analyst for 'Blinkit'. "
            "Your task is to answer specific business questions about user behavior using ONLY the provided user feedback contexts.\n\n"
            "CRITICAL RULES:\n"
            "1. Base your answer strictly on the provided context. Do not use outside knowledge.\n"
            "2. If the provided context does not contain sufficient information to answer the question, output exactly: {\"error\": \"Insufficient Data\"}\n"
            "3. Output your response STRICTLY as a valid JSON object matching this schema:\n"
            "{\n"
            "  \"insights\": [\n"
            "    {\n"
            "      \"theme\": \"Short title of the behavioral driver/friction point\",\n"
            "      \"description\": \"Detailed explanation based on context\",\n"
            "      \"confidence_score\": \"High/Medium/Low based on how many reviews corroborate this theme\",\n"
            "      \"corroborating_sources\": [list of review numbers, e.g., 1, 3, 5]\n"
            "    }\n"
            "  ],\n"
            "  \"actionable_recommendations\": [\"list of recommendations for product managers\"]\n"
            "}\n"
            "4. DO NOT output any markdown blocks, conversational text, or anything outside the JSON object. Just the raw JSON.\n"
            "5. DO NOT mention review numbers (e.g., 'In Review 1...') inside the description text. The description must be clean, narrative prose. Source linking is ONLY done via the corroborating_sources array."
        )
        
        user_prompt = f"Business Question: {question}\n\nRetrieved Contexts:\n{context_str}\n\nProvide your detailed behavioral analysis:"
        
        print(f"Sending prompt to Groq API ({self.model})...")
        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2, # Low temperature for more analytical/factual responses
            max_tokens=1024,
        )
        
        return completion.choices[0].message.content
