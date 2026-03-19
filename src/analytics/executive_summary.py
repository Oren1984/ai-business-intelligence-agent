# src/analytics/executive_summary.py — NeuroOps Insight Engine
# Generates LLM-powered executive summaries from metrics and auto-insights.

from src.analytics.analytics import (
    feature_usage_stats,
    inactive_users,
    error_frequency_stats,
    support_ticket_stats,
    user_activity_stats,
)
from src.analytics.auto_insights import build_auto_insights
from src.llm.provider import LLMProvider

def generate_executive_summary():
    feature_df = feature_usage_stats()
    inactive_df = inactive_users(days=7)
    error_df = error_frequency_stats()
    tickets_df = support_ticket_stats()
    activity_df = user_activity_stats()
    insights = build_auto_insights()

    top_feature = feature_df.iloc[0]["feature_used"] if not feature_df.empty else "N/A"
    top_feature_count = int(feature_df.iloc[0]["usage_count"]) if not feature_df.empty else 0

    top_error = error_df.iloc[0]["event_type"] if not error_df.empty else "N/A"
    top_error_count = int(error_df.iloc[0]["error_count"]) if not error_df.empty else 0

    open_tickets = int(tickets_df[tickets_df["status"] == "open"]["count"].sum()) if not tickets_df.empty else 0
    inactive_count = int(len(inactive_df))
    active_users = int(len(activity_df[activity_df["total_events"] > 0])) if not activity_df.empty else 0
    total_users = int(len(activity_df)) if not activity_df.empty else 0

    context = f"""
Current BI Metrics:
- Top feature: {top_feature} ({top_feature_count} events)
- Inactive users: {inactive_count}
- Top error: {top_error} ({top_error_count} occurrences)
- Open tickets: {open_tickets}
- Active users: {active_users}/{total_users}

Auto Insights:
""" + "\n".join([f"- {item['title']}: {item['message']}" for item in insights])

    system_prompt = (
        "You are an executive business intelligence assistant. "
        "Write a concise executive summary for product, support, and operations leaders. "
        "Focus on business meaning, risk, and next actions."
    )

    user_prompt = (
        "Create a short executive summary with three sections: "
        "1) Current State "
        "2) Key Risks "
        "3) Recommended Actions"
    )

    llm = LLMProvider()
    summary = llm.generate(system_prompt=system_prompt, user_prompt=user_prompt, context=context)

    return {
        "summary": summary,
        "context": context
    }
