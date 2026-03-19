# NeuroOps Insight Engine

AI-powered business intelligence platform for operational insights, decision support, and automated business workflows.

The NeuroOps Insight Engine combines structured analytics, SQL-style querying, LLM-generated explanations, retrieval-augmented context (RAG), executive summaries, and automation via n8n — all in a unified, demo-ready system.

---

## Core Capabilities

- Structured business analytics over product and system activity  
- SQL-style business question answering  
- LLM-powered explanations (Demo / OpenAI / Ollama modes)  
- Retrieval-Augmented Generation (RAG) using local knowledge base  
- Executive summary generation for business stakeholders  
- Automation handoff via n8n workflows  
- Interactive Streamlit dashboard for exploration and monitoring  

---

## Project Components

This system integrates:

- Business analytics engine  
- SQL-style reasoning agent  
- LLM abstraction layer  
- Retrieval (RAG) engine  
- Executive summary generator  
- Automation layer (n8n integration)  
- Streamlit UI  

---

## Project Structure

```text
neuroops-insight-engine/
│
├── data/                # Business datasets + RAG knowledge base
├── src/
│   ├── agent/           # SQL-style BI agent
│   ├── analytics/       # Metrics, insights, summaries
│   ├── dashboard/       # Streamlit UI
│   ├── llm/             # LLM provider abstraction
│   ├── rag/             # Retrieval system
│   └── integrations/    # n8n automation integration
│
├── docker/              # Docker setup
├── n8n/                 # Automation workflows
│
├── main.py              # CLI entrypoint
├── requirements.txt
├── .env.example
└── README.md
```

---

## Data Sources

The system operates on four main business datasets:

- users.csv
- usage_events.csv
- system_events.csv
- tickets.csv

These are loaded into SQLite and power the analytics, agent reasoning, and summary layers.

## UI Sections

### Overview

Business KPIs, usage trends, system errors, and support data.

### LLM Agent

Ask business questions and receive:

- SQL-style reasoning
- Data results
- Natural-language explanations
- RAG
- Enrich answers with internal business knowledge

### Automation

Generate structured payloads and simulate automation workflows via n8n.

### Executive Summary

High-level business insights, risks, and recommendations.

---

## Architecture Overview

The platform consists of:

- CSV data ingestion

- SQLite business data layer

- Analytics + insights engine

- SQL-style reasoning agent

- LLM provider abstraction

- RAG retrieval system

- Executive summary generator

- Automation layer (n8n)

- Streamlit UI

---

## Run Locally

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux

python main.py
streamlit run src/dashboard/dashboard.py
```

---

## Run with Docker

```bash
docker compose -f docker/docker-compose.yml up --build
```

---

## Environment Configuration

```bash
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
```

### Key Variables

```bash
LLM_PROVIDER=demo|openai|ollama
LLM_MODEL=...
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://api.openai.com/v1
OLLAMA_BASE_URL=http://localhost:11434
N8N_ENABLED=true|false
N8N_WEBHOOK_URL=http://localhost:5678/webhook/ai-bi-summary
```

---

## LLM Modes

### Demo

No external dependencies — fully local.

### OpenAI

Uses the OpenAI Responses API. Requires `OPENAI_API_KEY`.

### Ollama

Runs locally via Ollama.

---

## n8n Integration

- Demo-first automation design

- Payload generation inside UI

- Optional webhook activation

Example workflow:

```bash
n8n/demo_bi_webhook_workflow.json
```

---

## Example Business Questions

- What is the most used feature?

- Which users are inactive?

- Which errors occur most frequently?

- How many open tickets exist?

- What risks should we address right now?

---

## Docker Services

| Service | Description | Port |
|---------|-------------|------|
| `insight-engine` | Streamlit BI dashboard | http://localhost:8501 |
| `n8n` | Automation workflow engine | http://localhost:5678 |

---

## Notes

- Local-first architecture

- Demo-ready without external APIs

- Lightweight infrastructure (SQLite + Streamlit)

- Focused on clarity, explainability, and usability

---

## Summary

NeuroOps Insight Engine demonstrates how modern business intelligence can evolve into an AI-driven decision platform by combining analytics, reasoning, retrieval, and automation into a single cohesive system.

---

## License

MIT (see LICENSE)

---
