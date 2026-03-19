# src/integrations/n8n_client.py — NeuroOps Insight Engine
# Builds structured n8n webhook payloads and handles demo/live delivery.

import os
import requests
from datetime import datetime

def build_n8n_payload(insights, executive_summary):
    return {
        "event": "ai_bi_summary",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "neuroops-insight-engine",
        "insights": insights,
        "executive_summary": executive_summary,
    }

def send_to_n8n(payload):
    webhook_url = os.getenv("N8N_WEBHOOK_URL", "").strip()
    enabled = os.getenv("N8N_ENABLED", "false").strip().lower() == "true"

    if not webhook_url or not enabled:
        return {
            "mode": "demo",
            "status": "not_sent",
            "message": "n8n demo mode active. Set N8N_ENABLED=true and N8N_WEBHOOK_URL to enable live webhook delivery.",
            "payload": payload
        }

    try:
        response = requests.post(webhook_url, json=payload, timeout=30)
        return {
            "mode": "live",
            "status": response.status_code,
            "message": response.text[:1000],
            "payload": payload
        }
    except Exception as e:
        return {
            "mode": "error",
            "status": "failed",
            "message": str(e),
            "payload": payload
        }
