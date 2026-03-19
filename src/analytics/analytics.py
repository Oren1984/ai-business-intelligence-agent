# src/analytics/analytics.py — NeuroOps Insight Engine
# Core analytics functions: feature usage, user activity, errors, tickets, trends.

import pandas as pd
from datetime import timedelta
from src.data_loader.loader import load_csvs

def feature_usage_stats():
    _, usage, _, _ = load_csvs()
    return (
        usage.groupby("feature_used")
        .size()
        .reset_index(name="usage_count")
        .sort_values("usage_count", ascending=False)
    )

def user_activity_stats():
    users, usage, _, _ = load_csvs()
    activity = (
        usage.groupby("user_id")
        .agg(
            total_events=("event_id", "count"),
            total_duration=("duration", "sum"),
            last_activity=("timestamp", "max")
        )
        .reset_index()
    )
    merged = users.merge(activity, on="user_id", how="left")
    merged["total_events"] = merged["total_events"].fillna(0).astype(int)
    merged["total_duration"] = merged["total_duration"].fillna(0).astype(int)
    return merged

def error_frequency_stats():
    _, _, system, _ = load_csvs()
    return (
        system.groupby("event_type")
        .size()
        .reset_index(name="error_count")
        .sort_values("error_count", ascending=False)
    )

def inactive_users(days=7):
    users, usage, _, _ = load_csvs()
    latest_ts = usage["timestamp"].max()
    threshold = latest_ts - timedelta(days=days)

    last_activity = (
        usage.groupby("user_id")["timestamp"]
        .max()
        .reset_index(name="last_activity")
    )

    merged = users.merge(last_activity, on="user_id", how="left")
    inactive = merged[(merged["last_activity"].isna()) | (merged["last_activity"] < threshold)]
    return inactive.sort_values(["last_activity", "user_id"], ascending=[True, True])

def support_ticket_stats():
    _, _, _, tickets = load_csvs()
    summary = (
        tickets.groupby(["category", "status"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    return summary

def activity_trend():
    _, usage, _, _ = load_csvs()
    trend = usage.copy()
    trend["date"] = trend["timestamp"].dt.date
    return (
        trend.groupby("date")
        .size()
        .reset_index(name="events_count")
        .sort_values("date")
    )
