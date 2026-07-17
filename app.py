import streamlit as st
import json
import re
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from src.rag.retriever import SemanticRetriever
from src.rag.generator import InsightGenerator

st.set_page_config(page_title="Blinkit Pulse Discovery Engine", page_icon="⚡", layout="wide")

st.title("⚡ Blinkit Pulse: Behavioral Discovery Engine")
st.markdown("An enterprise-grade Product Manager's Command Center for unstructured feedback analysis.")

@st.cache_resource
def load_ai_models():
    return SemanticRetriever(), InsightGenerator()

try:
    retriever, generator = load_ai_models()
except Exception as e:
    st.error(f"Error initializing models: {e}. Please check your API keys.")
    st.stop()

# Sidebar Controls
st.sidebar.header("⚙️ Engine Controls")
st.sidebar.markdown("Filter the database before running AI analysis to enforce strict relevance.")
category_filter = st.sidebar.selectbox("Category Filter", ["All", "ui_ux", "customer_support", "delivery", "pricing", "quality", "search"])
top_k_limit = st.sidebar.slider("Context Limit (Reviews)", min_value=5, max_value=25, value=10, step=5)

query = st.text_input("Enter a business question (e.g., 'Why do users abandon their carts?'):", placeholder="Type your query here...")

if query:
    with st.spinner("Analyzing Blinkit Behavior..."):
        try:
            contexts = retriever.search(query=query, top_k=top_k_limit, filter_tag=category_filter)
            
            if not contexts:
                st.warning("No relevant context found in the database.")
            else:
                analysis_raw = generator.generate_insight(question=query, retrieved_contexts=contexts)
                
                # Parse JSON
                clean_json = re.sub(r'```json\n|```\n?', '', analysis_raw).strip()
                data = json.loads(clean_json)
                
                if "error" in data:
                    st.error(f"Error: {data['error']}")
                else:
                    # Layout
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader("💡 Behavioral Insights")
                        
                        insights = data.get('insights', [])
                        for idx, insight in enumerate(insights):
                            st.markdown(f"### {idx+1}. {insight.get('theme', 'Unknown Theme')}")
                            
                            # Create inner columns for description vs chart
                            inner_col1, inner_col2 = st.columns([3, 1])
                            
                            with inner_col1:
                                st.write(insight.get('description', ''))
                                
                                # Traceability Engine
                                with st.expander("🔍 View Corroborating Evidence"):
                                    sources = insight.get('corroborating_sources', [])
                                    if sources:
                                        for s_id in sources:
                                            # Handle zero-based indexing in array if LLM returns 1-based review index
                                            try:
                                                idx_num = int(s_id) - 1
                                                if 0 <= idx_num < len(contexts):
                                                    st.info(f"**Review {s_id}:** {contexts[idx_num]['text']}")
                                                else:
                                                    st.warning(f"Source ID {s_id} out of bounds.")
                                            except ValueError:
                                                st.write(str(s_id))
                                    else:
                                        st.write("No specific sources cited.")
                                        
                            with inner_col2:
                                # Confidence Score Gauge
                                conf_str = str(insight.get('confidence_score', '')).lower()
                                val = 90 if 'high' in conf_str else 60 if 'medium' in conf_str else 30
                                
                                fig_gauge = go.Figure(go.Indicator(
                                    mode = "gauge+number",
                                    value = val,
                                    title = {'text': "Confidence", 'font': {'size': 14}},
                                    number = {'font': {'size': 24}},
                                    gauge = {
                                        'axis': {'range': [0, 100]},
                                        'bar': {'color': "green" if val > 60 else "orange" if val > 30 else "red"},
                                    }
                                ))
                                fig_gauge.update_layout(height=120, margin=dict(l=10, r=10, t=30, b=10))
                                st.plotly_chart(fig_gauge, use_container_width=True, key=f"gauge_{idx}")
                            
                            st.divider()

                    with col2:
                        st.subheader("📊 Data Distribution")
                        
                        # Generate Keyword Distribution Bar Chart
                        all_tags = []
                        for ctx in contexts:
                            all_tags.extend(ctx.get('tags', []))
                            
                        if all_tags:
                            df_tags = pd.DataFrame({'Keyword': all_tags})
                            counts = df_tags['Keyword'].value_counts().reset_index()
                            counts.columns = ['Keyword', 'Count']
                            
                            fig_bar = px.bar(counts, x='Keyword', y='Count', title="Keyword Mentions in Retrieved Context", color='Keyword')
                            st.plotly_chart(fig_bar, use_container_width=True)
                        else:
                            st.write("No keyword tags found in the retrieved context.")
                        
                        st.subheader("🎯 Actionable Recommendations")
                        for rec in data.get('actionable_recommendations', []):
                            st.success(f"- {rec}")
                            
        except Exception as e:
            st.error(f"An error occurred: {e}")
