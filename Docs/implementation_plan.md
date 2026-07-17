# Phase-Wise Implementation Plan: Blinkit Pulse Behavioral Discovery Engine

This document outlines the step-by-step implementation strategy for building the AI-Powered Discovery Engine based on the established `context.md` and `architecture.md`.

---

## Phase 1: Setup & Data Ingestion
**Goal:** Establish the foundation and begin collecting raw user feedback from diverse sources.

- **Step 1.1: Project Setup & Tools Configuration**
  - Initialize the project repository.
  - Set up Groq API keys (as the primary free AI provider).
  - Create a dedicated Google Workspace/Notion workspace for the database.
- **Step 1.2: Build Python Scrapers**
  - **Google Play Store (App Reviews):** Use `google-play-scraper` (Python) to fetch Blinkit app reviews for free.
  - **Social Media (Twitter/X & Reddit):** Use free tools like `ntscraper` (for Twitter/X mentions). For Reddit, use **keyless scraping** via custom HTML parsing (e.g., `BeautifulSoup`) as a fallback, while waiting for official API access via the Reddit Help Center (per their 2026 Developer Policy).
  - **Video Comments (YouTube):** Use the official free tier of the **YouTube Data API v3** to easily and reliably fetch thousands of YouTube reviews.
  - **Consumer Review Websites:** Use `BeautifulSoup` to parse and scrape free review platforms like MouthShut and Trustpilot.
- **Step 1.3: Data Normalization & Formatting**
  - Standardize scraped data into a normalized JSON schema containing: `text`, `timestamp`, `source`, `author`, and `rating`.

---

## Phase 2: Data Pre-Processing, Normalization & Chunking
**Goal:** Clean the raw data without destroying semantic value, tag for intent, and format into metadata-rich chunks for semantic search.

- **Step 2.1: Platform-Specific Parsing**
  - **Why it's critical:** Different platforms format text differently. Stripping it universally destroys context.
  - Resolve Reddit nested threads into conversational formats (e.g., "User A: ... User B: ...").
  - Clean up excessive X (Twitter) handles (`@username`) while strictly preserving intent-driven hashtags (e.g., `#BlinkitDelivery`).
- **Step 2.2: Noise Reduction & Emoji Handling**
  - **Why it's critical:** Emojis contain high-density sentiment. Stripping a "😡" removes the core emotion of the review.
  - Instead of stripping emojis, use Python's `emoji` library to translate them into text aliases (e.g., `:pouting_face:`). The LLM processes text aliases perfectly as sentiment markers.
- **Step 2.3: Intent & Keyword Pre-Filtering**
  - **Why it's critical:** Pre-tagging data drastically improves RAG retrieval speed and precision when answering specific business questions.
  - Introduce a tagging mechanism to identify and tag records containing specific behavioral keywords (e.g., `electronics`, `pricing`, `search`, `delivery`, `UI`).
- **Step 2.4: Spam Filtering & Length Adjustments**
  - Use less aggressive length filtering. Discard only complete spam or gibberish, preserving short but highly semantic feedback (e.g., "App crashes on search").
- **Step 2.5: Hybrid Chunking & Lean Metadata**
  - **Why it's critical:** App reviews are inherently short. A tiny chunk size destroys their context. Massive Reddit posts break embedding limits. A hybrid chunking strategy balances both.
  - Split text using `langchain_text_splitters` (`RecursiveCharacterTextSplitter`) with a large `chunk_size` of `1000`. This guarantees 99% of short App Store reviews remain fully intact, while safely splitting massive essays.
  - Strip bloated metadata. The finalized JSON array will focus purely on semantic intent and map chunks to only three essential keys: `rating`, `keyword_tags`, and `text_chunk`.

---

## Phase 3: Embedding & Vector Storage
**Goal:** Convert text chunks into embeddings to enable scalable semantic search.

- **Step 3.1: Generate Embeddings**
  - Use a free local embedding model like HuggingFace's `all-MiniLM-L6-v2` (via `sentence-transformers`) to convert the text chunks into vectors.
- **Step 3.2: Vector Database Setup**
  - Initialize a local `ChromaDB` instance or set up a free tier `Pinecone` index.
- **Step 3.3: Data Ingestion to DB**
  - Push the generated embeddings along with their metadata (original text, source, timestamp) into the Vector DB.

---

## Phase 4: AI Processing & Retrieval-Augmented Generation (RAG)
**Goal:** Extract behavioral themes using an LLM on demand.

- **Step 4.1: Core Python Controller (`main.py`)**
  - Create a main Python script that acts as the entry point, allowing you to run the entire pipeline on command.
- **Step 4.2: Semantic Retrieval**
  - The Python script queries the Vector DB for chunks most relevant to the question (e.g., "Why do users avoid new categories?").
- **Step 4.3: LLM Integration & Prompt Engineering**
  - Pass the retrieved context directly to the Groq API.
  - Craft system prompts instructing the LLM to synthesize the retrieved chunks and identify psychological drivers and pain points.

---

## Phase 5: Validation & Quality Control
**Goal:** Ensure the insights are trustworthy and traceable.

- **Step 5.1: Clean Source-Linking Implementation**
  - Force the LLM (via prompt engineering) to strictly exclude source IDs from the human-readable text to keep the response clean. Instead, the LLM must append the original source IDs only in a dedicated `corroborating_sources` metadata array inside the JSON object.
- **Step 5.2: Hallucination Checks**
  - Implement a confidence scoring mechanism based on the number of retrieved chunks corroborating a specific theme.

---

## Phase 6: Interactive Web UI (Streamlit)
**Goal:** Provide an interactive, live web application that acts as an enterprise-grade Product Manager's Command Center, allowing graduation judges to test the RAG engine themselves.

- **Step 6.1: Build the Streamlit App (`app.py`)**
  - Create a user-friendly frontend using the `streamlit` library.
  - Expose a search bar where users can type business questions.
  - **Elevate the UX with a Loader:** Implement a loading state using `st.spinner` (or a custom loader) while the API processes the data. Strictly avoid using any text-streaming or typewriter effects; wait until the final structured data is ready, then render it all at once to provide a clean and professional UX.
  - Display the JSON-validated AI response in clean, readable UI cards (showing themes and descriptions).
- **Step 6.2: Build a "Traceability Engine" (Show Your Work)**
  - Beneath each generated insight, implement an interactive `st.expander` titled "🔍 View Corroborating Evidence".
  - When clicked, this must reveal the raw, scraped user reviews used by the RAG pipeline to generate that specific insight, proving accuracy and preventing hallucination concerns.
- **Step 6.3: Implement Visual Data Storytelling**
  - Use Streamlit's native integration with **Plotly** or **Altair** (both free) to parse the JSON metadata and generate live charts.
  - Generate a **"Confidence Score" gauge chart** for every extracted theme to visually represent data reliability.
  - Generate a **bar chart** displaying the distribution of keyword tags (e.g., UI, Pricing, Delivery) across the retrieved feedback.
- **Step 6.4: Cloud Deployment**
  - Host the application for free on Streamlit Community Cloud.
  - Securely manage API keys (`PINECONE_API_KEY`, `GROQ_API_KEY`) via Streamlit Secrets rather than exposing them in the repo.
  - Provide a live public URL (e.g., `https://blinkit-pulse.streamlit.app`) for the jury.

---

## Phase 7: Final Deliverables
**Goal:** Package the work for stakeholder review as per the project requirements.

- **Step 7.1: Workflow Link**
  - Finalize and share the public, testable link to the automated pipeline.
- **Step 7.2: Architecture 1-Slider**
  - Create the presentation slide visually outlining the AI workflow for the final project deck.
