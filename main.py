# main.py — NeuroOps Insight Engine
# CLI entry point. Initializes the platform, runs core analytics,
# and demonstrates all AI layers: agent, RAG, LLM, executive summary, n8n.

import os
from dotenv import load_dotenv
load_dotenv()

from src.data_loader.loader import init_sqlite
from src.analytics.analytics import (
    feature_usage_stats,
    user_activity_stats,
    error_frequency_stats,
    inactive_users,
    support_ticket_stats,
)
from src.analytics.insight_engine import generate_insights
from src.analytics.auto_insights import build_auto_insights
from src.analytics.executive_summary import generate_executive_summary
from src.agent.agent import BusinessIntelligenceAgent
from src.llm.provider import LLMProvider
from src.rag.retriever import retrieve_context
from src.integrations.n8n_client import build_n8n_payload

def main():
    print("=" * 80)
    print("NEUROOPS INSIGHT ENGINE")
    print("=" * 80)

    init_sqlite()

    print("\n[1] Core Analytics")
    print(feature_usage_stats().to_string(index=False))
    print(error_frequency_stats().to_string(index=False))
    print(user_activity_stats().to_string(index=False))

    print("\n[2] Inactive Users")
    inactive = inactive_users(days=7)
    print(inactive.to_string(index=False) if not inactive.empty else "No inactive users found.")

    print("\n[3] Support Tickets")
    print(support_ticket_stats().to_string(index=False))

    print("\n[4] Rule-Based Insights")
    for item in generate_insights():
        print(f"- {item}")

    print("\n[5] Auto Insights")
    for item in build_auto_insights():
        print(f"- [{item['severity'].upper()}] {item['title']}: {item['message']}")

    print("\n[6] Agent Demo")
    agent = BusinessIntelligenceAgent()
    question = "Which errors appear most often?"
    sql, df, explanation = agent.ask(question)
    print("Question:", question)
    print("SQL:\n", sql)
    print("Explanation:", explanation)
    print(df.to_string(index=False))

    print("\n[7] RAG Demo")
    retrieval = retrieve_context("What should product teams do about inactive users?")
    llm = LLMProvider()
    rag_answer = llm.generate(
        system_prompt="You are a business intelligence assistant.",
        user_prompt="What should product teams do about inactive users?",
        context=retrieval["context"]
    )
    print(rag_answer)

    print("\n[8] Executive Summary")
    summary_obj = generate_executive_summary()
    print(summary_obj["summary"])

    print("\n[9] n8n Payload Preview")
    payload = build_n8n_payload(build_auto_insights(), summary_obj["summary"])
    print(payload)

if __name__ == "__main__":
    main()
