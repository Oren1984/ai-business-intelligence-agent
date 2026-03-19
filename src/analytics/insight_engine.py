# src/analytics/insight_engine.py — NeuroOps Insight Engine
# Rule-based insight generation from key business metrics.

from src.analytics.analytics import (
    feature_usage_stats,
    inactive_users,
    error_frequency_stats,
    support_ticket_stats,
    user_activity_stats,
)

def generate_insights():
    feature_df = feature_usage_stats()
    inactive_df = inactive_users(days=7)
    error_df = error_frequency_stats()
    tickets_df = support_ticket_stats()
    activity_df = user_activity_stats()

    insights = []

    if not feature_df.empty:
        top_feature = feature_df.iloc[0]
        insights.append(
            f"Most used feature: {top_feature['feature_used']} ({top_feature['usage_count']} usages)"
        )

    insights.append(f"Inactive users detected: {len(inactive_df)}")

    if not error_df.empty:
        top_error = error_df.iloc[0]
        insights.append(
            f"Most frequent system error: {top_error['event_type']} ({top_error['error_count']} events)"
        )

    open_tickets = tickets_df[tickets_df["status"] == "open"]["count"].sum() if not tickets_df.empty else 0
    insights.append(f"Open support tickets: {int(open_tickets)}")

    total_users = len(activity_df)
    active_users = len(activity_df[activity_df["total_events"] > 0])
    insights.append(f"Active users: {active_users} / {total_users}")

    return insights
