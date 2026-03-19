# src/dashboard/dashboard.py — NeuroOps Insight Engine
# Streamlit UI: Overview, Agent, RAG, Automation, Executive Summary.

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from src.data_loader.loader import init_sqlite
from src.analytics.analytics import (
    feature_usage_stats,
    error_frequency_stats,
    inactive_users,
    activity_trend,
    support_ticket_stats,
    user_activity_stats,
)
from src.analytics.insight_engine import generate_insights
from src.analytics.auto_insights import build_auto_insights
from src.analytics.executive_summary import generate_executive_summary
from src.agent.agent import BusinessIntelligenceAgent
from src.llm.provider import LLMProvider
from src.rag.retriever import retrieve_context
from src.integrations.n8n_client import build_n8n_payload, send_to_n8n

st.set_page_config(
    page_title="NeuroOps Insight Engine",
    page_icon="🧠",
    layout="wide",
)
init_sqlite()

provider_name = os.getenv("LLM_PROVIDER", "demo")
model_name = os.getenv("LLM_MODEL", "gpt-4.1-mini")
n8n_enabled = os.getenv("N8N_ENABLED", "false")

st.title("🧠 NeuroOps Insight Engine")
st.caption("Analytics · LLM Agent · RAG · Executive Summary · n8n Automation")

with st.sidebar:
    st.header("Configuration")
    st.write(f"**LLM Provider:** `{provider_name}`")
    st.write(f"**LLM Model:** `{model_name}`")
    st.write(f"**n8n Enabled:** `{n8n_enabled}`")
    st.divider()
    st.info("Demo mode works without API keys. Configure LLM_PROVIDER in `.env` to switch providers.")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Agent",
    "RAG",
    "Automation",
    "Executive Summary",
])

# ── TAB 1: OVERVIEW ─────────────────────────────────────────────────────────
with tab1:
    st.subheader("Business Overview")
    insights = generate_insights()
    auto_insights = build_auto_insights()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Key Insights")
        for item in insights:
            st.write(f"- {item}")

    with col2:
        st.markdown("### Auto Insights")
        for item in auto_insights:
            badge = "⚠️" if item["severity"] == "warning" else "ℹ️"
            st.write(f"{badge} **{item['title']}** — {item['message']}")

    with col3:
        st.markdown("### Inactive Users (7d)")
        inactive_df = inactive_users(days=7)
        if inactive_df.empty:
            st.success("No inactive users detected.")
        else:
            st.dataframe(inactive_df, use_container_width=True)

    st.divider()

    left, right = st.columns(2)

    with left:
        st.markdown("### Feature Usage")
        feature_df = feature_usage_stats()
        st.dataframe(feature_df, use_container_width=True)
        if not feature_df.empty:
            st.bar_chart(feature_df.set_index("feature_used"))

        st.markdown("### Error Distribution")
        error_df = error_frequency_stats()
        st.dataframe(error_df, use_container_width=True)
        if not error_df.empty:
            st.bar_chart(error_df.set_index("event_type"))

    with right:
        st.markdown("### Activity Trend")
        trend_df = activity_trend()
        st.dataframe(trend_df, use_container_width=True)
        if not trend_df.empty:
            temp = trend_df.copy()
            temp["date"] = temp["date"].astype(str)
            st.line_chart(temp.set_index("date"))

        st.markdown("### Support Tickets")
        st.dataframe(support_ticket_stats(), use_container_width=True)

        st.markdown("### User Activity")
        st.dataframe(user_activity_stats(), use_container_width=True)

# ── TAB 2: AGENT ────────────────────────────────────────────────────────────
with tab2:
    st.subheader("LLM Business Agent")
    st.caption("Ask a business question. The agent generates SQL, runs it, and explains the result.")

    q = st.text_input(
        "Business question",
        value="What is the most used feature?",
        placeholder="e.g. Which errors appear most often?",
    )

    supported = (
        "- What is the most used feature?\n"
        "- Which users are inactive?\n"
        "- Which errors appear most often?\n"
        "- How many open tickets exist?\n"
        "- What are the top countries by signup count?"
    )
    with st.expander("Supported questions"):
        st.markdown(supported)

    if st.button("Run Agent", type="primary"):
        with st.spinner("Running agent…"):
            agent = BusinessIntelligenceAgent()
            sql, df, explanation = agent.ask(q)

            llm = LLMProvider()
            llm_answer = llm.generate(
                system_prompt="You are a business intelligence assistant. Explain data results clearly for a business stakeholder.",
                user_prompt=q,
                context=f"SQL:\n{sql}\n\nResult:\n{df.to_string(index=False) if not df.empty else 'No rows'}\n\nBase Explanation:\n{explanation}",
            )

        st.markdown("### Generated SQL")
        st.code(sql, language="sql")

        st.markdown("### Query Result")
        if df.empty:
            st.info("No data returned.")
        else:
            st.dataframe(df, use_container_width=True)

        st.markdown("### Agent Explanation")
        st.write(explanation)

        st.markdown("### LLM Explanation")
        st.write(llm_answer)

# ── TAB 3: RAG ──────────────────────────────────────────────────────────────
with tab3:
    st.subheader("RAG — Knowledge-Augmented Q&A")
    st.caption("Retrieves relevant business documents, then generates a context-aware answer.")

    rag_q = st.text_input(
        "Business question",
        value="What business risks should we care about if reports are failing often?",
    )

    if st.button("Run RAG Answer", type="primary"):
        with st.spinner("Retrieving context and generating answer…"):
            retrieval = retrieve_context(rag_q, top_k=3)
            context = retrieval["context"]

            llm = LLMProvider()
            rag_answer = llm.generate(
                system_prompt="You are a RAG-based business intelligence assistant. Use retrieved knowledge to answer clearly.",
                user_prompt=rag_q,
                context=context,
            )

        st.markdown("### Retrieved Sources")
        if retrieval["documents"]:
            for doc in retrieval["documents"]:
                st.write(f"- `{doc['source']}` (score: {doc['score']})")
        else:
            st.warning("No relevant documents found in the knowledge base.")

        with st.expander("Retrieved Context"):
            st.text_area("Context", value=context, height=260, label_visibility="collapsed")

        st.markdown("### RAG Answer")
        st.write(rag_answer)

# ── TAB 4: AUTOMATION ───────────────────────────────────────────────────────
with tab4:
    st.subheader("n8n Automation")
    st.caption("Preview the structured payload and optionally deliver it to an n8n webhook.")

    auto_insights = build_auto_insights()
    summary_obj = generate_executive_summary()
    payload = build_n8n_payload(auto_insights, summary_obj["summary"])

    st.markdown("### Outgoing Payload")
    st.json(payload)

    if st.button("Send to n8n", type="primary"):
        with st.spinner("Sending payload…"):
            result = send_to_n8n(payload)
        st.markdown("### Delivery Result")
        st.json(result)

    if n8n_enabled.lower() != "true":
        st.info("Demo mode active — payload is displayed but not sent. Set `N8N_ENABLED=true` and `N8N_WEBHOOK_URL` to enable live delivery.")

# ── TAB 5: EXECUTIVE SUMMARY ────────────────────────────────────────────────
with tab5:
    st.subheader("Executive Summary Generator")
    st.caption("Generates a business-focused summary with current state, risks, and recommended actions.")

    if st.button("Generate Executive Summary", type="primary"):
        with st.spinner("Generating summary…"):
            obj = generate_executive_summary()

        st.markdown("### Executive Summary")
        st.write(obj["summary"])

        with st.expander("Source Context"):
            st.text(obj["context"])
