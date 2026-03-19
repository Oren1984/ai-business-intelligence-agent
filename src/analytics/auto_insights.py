# src/analytics/auto_insights.py — NeuroOps Insight Engine
# Severity-tagged auto-insights derived from analytics metrics.

from src.analytics.analytics import (
    feature_usage_stats,
    inactive_users,
    error_frequency_stats,
    support_ticket_stats,
    user_activity_stats,
    activity_trend,
)

def build_auto_insights():
    feature_df = feature_usage_stats()
    inactive_df = inactive_users(days=7)
    error_df = error_frequency_stats()
    tickets_df = support_ticket_stats()
    activity_df = user_activity_stats()
    trend_df = activity_trend()

    insights = []

    if not feature_df.empty:
        top_feature = feature_df.iloc[0]
        insights.append({
            "title": "Top Feature",
            "severity": "info",
            "message": f"{top_feature['feature_used']} is the most used feature with {int(top_feature['usage_count'])} events."
        })

    if len(inactive_df) > 0:
        insights.append({
            "title": "Inactive Users",
            "severity": "warning",
            "message": f"{len(inactive_df)} users are inactive in the current analysis window."
        })

    if not error_df.empty:
        top_error = error_df.iloc[0]
        severity = "warning" if int(top_error["error_count"]) >= 2 else "info"
        insights.append({
            "title": "Most Frequent Error",
            "severity": severity,
            "message": f"{top_error['event_type']} appears {int(top_error['error_count'])} times."
        })

    open_tickets = 0
    if not tickets_df.empty:
        open_tickets = int(tickets_df[tickets_df["status"] == "open"]["count"].sum())

    insights.append({
        "title": "Open Tickets",
        "severity": "warning" if open_tickets > 0 else "info",
        "message": f"There are {open_tickets} open support tickets."
    })

    active_users = int(len(activity_df[activity_df["total_events"] > 0])) if not activity_df.empty else 0
    total_users = int(len(activity_df)) if not activity_df.empty else 0
    insights.append({
        "title": "User Activity Coverage",
        "severity": "info",
        "message": f"{active_users} out of {total_users} users generated activity events."
    })

    if not trend_df.empty:
        delta = int(trend_df["events_count"].iloc[-1] - trend_df["events_count"].iloc[0])
        direction = "up" if delta > 0 else "down" if delta < 0 else "flat"
        insights.append({
            "title": "Activity Trend",
            "severity": "info",
            "message": f"Activity trend is {direction} across the visible timeline."
        })

    return insights
