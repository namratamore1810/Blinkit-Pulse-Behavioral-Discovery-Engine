# Edge Cases & Mitigation Strategy: Blinkit Pulse Behavioral Discovery Engine

When building an automated data pipeline that relies on web scraping and Large Language Models, various edge cases can disrupt the system. This document outlines potential edge cases across the pipeline and strategies to mitigate them.

---

## 1. Data Ingestion & Scraping Edge Cases

### 1.1. Rate Limiting, IP Bans, and API Restrictions
- **Scenario:** The scraping scripts trigger bot detection (e.g., Trustpilot returning a `403 Forbidden` error) or platform API policies change (e.g., Reddit 2026 Developer Policy blocking unauthenticated scraping).
- **Mitigation:** 
  - For bot protection (Trustpilot), implement gracefully catching the `403` exception so the rest of the pipeline continues without crashing.
  - For strict API gating (Reddit), rely on official support ticket requests for research access or fall back to limited keyless HTML parsing.
  - Implement randomized delays (e.g., `time.sleep(random.uniform(2, 5))`) between requests.
  - Set a conservative maximum limit on the number of reviews scraped per day per source.

### 1.2. Platform API/DOM Structure Changes
- **Scenario:** A platform like Trustpilot or MouthShut changes its HTML structure, breaking the `BeautifulSoup` parsing logic.
- **Mitigation:** 
  - Implement `try-except` blocks around parsing logic to gracefully catch `AttributeError`.
  - Send an automated alert (via email or webhook) if a scraper returns 0 results for two consecutive days.

### 1.3. Multi-Lingual and "Hinglish" Feedback
- **Scenario:** Since Blinkit is an Indian app, many reviews are written in regional languages or "Hinglish" (Hindi written in English script), which might confuse the embedding model or LLM.
- **Mitigation:** 
  - The Groq API (using advanced models like Llama-3) is generally adept at understanding Hinglish. For embeddings, ensure the chosen HuggingFace model supports multilingual text (e.g., `paraphrase-multilingual-MiniLM-L12-v2`).

---

## 2. Pre-Processing & Chunking Edge Cases

### 2.1. Keyboard Mashing and Nonsensical Text
- **Scenario:** A user submits a 500-character review consisting of repeated letters (e.g., "aaaaaaaaaa") or random characters.
- **Mitigation:**
  - Implement a heuristic check during sanitization to discard text containing words longer than 20 characters or a very low ratio of valid dictionary words.

### 2.2. Context Loss During Chunking
- **Scenario:** A long, detailed Reddit post is split exactly in the middle of a sentence detailing a critical UI friction point, causing the embedding to lose semantic meaning.
- **Mitigation:**
  - When using `langchain_text_splitters`, configure a **chunk overlap** (e.g., chunk size of 300 words with an overlap of 50 words) to ensure context bridges across chunks.

---

## 3. Embedding & Vector Storage Edge Cases

### 3.1. Free-Tier Database Limits Exceeded
- **Scenario:** The Pinecone free tier reaches its index capacity (currently 1 project, max 100k vectors on starter), or the local ChromaDB runs out of immediate storage space.
- **Mitigation:**
  - Implement a Time-To-Live (TTL) or a rolling deletion mechanism to drop vector embeddings older than 6 months. Behavioral trends older than 6 months are less relevant to immediate product iterations anyway.

---

## 4. AI Processing & Automation (RAG) Edge Cases

### 4.1. LLM API Rate Limits
- **Scenario:** The Groq API free tier rate limit is reached during a bulk processing run.
- **Mitigation:**
  - Configure the n8n/Make.com automation layer to respect `Retry-After` headers. Use a queue mechanism to delay processing rather than failing the workflow completely.

### 4.2. Invalid JSON Output from LLM
- **Scenario:** The prompt asks the LLM to return insights in a strict JSON format, but it includes conversational text (e.g., "Here is the JSON you requested: {...}").
- **Mitigation:**
  - Use structured output modes if supported by the API.
  - Implement a regex parser in the automation engine to extract only the text between the first `{` or `[` and the last `}` or `]`.

### 4.3. Hallucination on Scarce Data
- **Scenario:** The LLM is asked to identify UI friction, but the retrieved chunks contain zero relevant information. The LLM invents a friction point to satisfy the prompt.
- **Mitigation:**
  - Explicitly instruct the LLM in the system prompt: *"If the provided context does not contain sufficient information to answer the question, output 'Insufficient Data' rather than guessing."*

---

## 5. Web UI & Deployment Edge Cases

### 5.1. Streamlit Cloud Memory Limits
- **Scenario:** The free tier of Streamlit Community Cloud has strict memory constraints (typically ~1GB). Loading large models locally would crash the app.
- **Mitigation:**
  - The vector embeddings are generated using the lightweight `all-MiniLM-L6-v2` model, which has a very small memory footprint. The heavy LLM processing is offloaded to the Groq API, ensuring the Streamlit app remains well within the 1GB memory limit.

### 5.2. Exposed API Keys in Public Repository
- **Scenario:** The source code must be pushed to a public GitHub repository for the graduation project, risking the leakage of `PINECONE_API_KEY` and `GROQ_API_KEY`.
- **Mitigation:**
  - The local environment uses a `.env` file (added to `.gitignore`). For the live app, keys will be exclusively injected through the **Streamlit Secrets Management** console, ensuring they are never hardcoded or exposed to the public.
