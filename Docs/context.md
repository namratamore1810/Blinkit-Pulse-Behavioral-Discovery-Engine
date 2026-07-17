# Context: Blinkit Pulse Behavioral Discovery Engine

## Background & Problem
Blinkit users have established habitual shopping patterns for essentials, leading to highly repetitive purchases and a lack of cross-category exploration. The Growth Team needs to understand the behavioral, psychological, and UI/UX barriers preventing discovery, but manual analysis of unstructured qualitative feedback is impossible at scale.

## Objective
Design and build an **AI-Powered Discovery Engine** (Part 1 of the project). This engine will act as an automated research assistant to ingest, process, and synthesize unstructured qualitative user feedback (from app stores, social media, forums, etc.) into actionable insights about shopping habits, friction points, and discovery behaviors.

## System Architecture & Workflow
1. **Data Aggregation**: Scrapes unstructured user feedback from diverse online sources.
2. **Data Sanitization & Tagging**: Cleans data via platform-specific parsing, translates emojis to text aliases for sentiment preservation, tags intents, and maps rich metadata to chunks.
3. **The Engine (RAG):** The system searches the vector database for relevant feedback and feeds it into the Llama-3 model via the Groq API. The LLM generates validated, structured JSON insights.
4. **The Interface (Streamlit Web UI):** The entire system is exposed via a live, interactive Streamlit web application for the judges to test.

## Key Questions to Answer
The system must automatically extract insights regarding:
- Why users stick to the same categories and what prevents exploration.
- How product discovery happens today.
- The role of habits in shopping behavior.
- Information needs and frustrations when trying new categories.
- High-experimentation user segments and unmet needs.
- UI/UX elements in Blinkit (e.g., "Past Orders") that discourage browsing.
- External triggers (e.g., viral trends) that prompt searches for new products.

## Validation & Quality Control
The system must include a methodology to validate AI-generated insights, such as source-linking and hallucination checks.

## Non-Goals
- Building the final consumer-facing feature (this comes in a later phase).
- Solving supply chain/logistics issues.
- Manual data entry or reading reviews manually.
- Generating quantitative metrics (DAU/MAU).

## Target Audience
- **Product Managers & Growth Teams**: For data-backed hypotheses.
- **User Researchers**: As a foundation for targeted primary research.
- **Business Strategy**: To increase the percentage of users buying from new categories.

## Expected Deliverables (Part 1)
1. **Live Web App Link**: A public, testable Streamlit URL (e.g., `https://blinkit-pulse.streamlit.app`) for the jury.
2. **Architecture 1-Slider**: A presentation slide visualizing the AI workflow from data source to insight generation.
