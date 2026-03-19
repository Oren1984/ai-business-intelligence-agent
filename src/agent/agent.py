# src/agent/agent.py — NeuroOps Insight Engine
# SQL-style BI agent: routes natural language questions to SQL queries with explanations.

import pandas as pd
from src.data_loader.loader import get_connection

class BusinessIntelligenceAgent:
    def __init__(self):
        self.conn = get_connection()

    def _run_query(self, sql: str) -> pd.DataFrame:
        return pd.read_sql_query(sql, self.conn)

    def ask(self, question: str):
        q = question.lower().strip()

        if "most used feature" in q:
            sql = """
            SELECT feature_used, COUNT(*) AS usage_count
            FROM usage_events
            GROUP BY feature_used
            ORDER BY usage_count DESC
            LIMIT 1
            """
            df = self._run_query(sql)
            if df.empty:
                return sql, df, "No feature usage data was found."
            row = df.iloc[0]
            explanation = f"The most used feature is '{row['feature_used']}' with {row['usage_count']} usage events."
            return sql, df, explanation

        if "inactive users" in q or "which users are inactive" in q:
            sql = """
            SELECT u.user_id, u.country, u.role, MAX(ue.timestamp) AS last_activity
            FROM users u
            LEFT JOIN usage_events ue ON u.user_id = ue.user_id
            GROUP BY u.user_id, u.country, u.role
            HAVING last_activity IS NULL OR last_activity < (
                SELECT datetime(MAX(timestamp), '-7 days') FROM usage_events
            )
            ORDER BY last_activity ASC
            """
            df = self._run_query(sql)
            explanation = f"{len(df)} inactive users were found based on no activity in the last 7 days of available usage history."
            return sql, df, explanation

        if "errors appear most often" in q or "most frequent error" in q:
            sql = """
            SELECT event_type, COUNT(*) AS error_count
            FROM system_events
            GROUP BY event_type
            ORDER BY error_count DESC
            LIMIT 1
            """
            df = self._run_query(sql)
            if df.empty:
                return sql, df, "No system error events were found."
            row = df.iloc[0]
            explanation = f"The most frequent error is '{row['event_type']}' with {row['error_count']} occurrences."
            return sql, df, explanation

        if "open tickets" in q:
            sql = """
            SELECT category, COUNT(*) AS open_count
            FROM tickets
            WHERE status = 'open'
            GROUP BY category
            ORDER BY open_count DESC
            """
            df = self._run_query(sql)
            explanation = f"There are {int(df['open_count'].sum()) if not df.empty else 0} open tickets in total."
            return sql, df, explanation

        if "top countries" in q or "countries by signup" in q:
            sql = """
            SELECT country, COUNT(*) AS users_count
            FROM users
            GROUP BY country
            ORDER BY users_count DESC
            """
            df = self._run_query(sql)
            explanation = "These are the top countries by number of signed-up users."
            return sql, df, explanation

        sql = "SELECT 'Unsupported question' AS message"
        df = self._run_query(sql)
        explanation = (
            "Supported questions: "
            "What is the most used feature? "
            "Which users are inactive? "
            "Which errors appear most often? "
            "How many open tickets exist? "
            "What are the top countries by signup count?"
        )
        return sql, df, explanation
