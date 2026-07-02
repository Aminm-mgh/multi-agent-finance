# Multi-Agent Financial Research System

A multi-agent AI system that autonomously analyses public companies using SEC filings, live financial data, and news — powered by LangGraph, RAG, and Claude.

Built as an academic project to answer: *can a team of specialised AI agents replace hours of manual financial research?*

---

## Research Questions

1. Does task decomposition across specialised agents produce more accurate, less hallucinated financial analysis than a single LLM?
2. How does RAG grounding on source documents reduce factual errors compared to LLM parametric memory alone?
3. What failure modes emerge in agent-to-agent handoffs — where does the pipeline break?
4. Can a critic agent meaningfully improve output quality, or does it introduce latency without accuracy gains?
5. How do you evaluate a multi-agent system rigorously beyond task completion rate?

---

## Architecture

Four specialised agents orchestrated by LangGraph:

| Agent | Role | Data Source |
|-------|------|-------------|
| Researcher | Fetches and chunks SEC 10-K/10-Q filings via RAG | SEC EDGAR |
| Analyst | Computes financial ratios and cross-references live data | Yahoo Finance |
| News | Fetches recent articles and analyses sentiment | NewsAPI |
| Critic | Cross-checks all agents, assigns confidence score | Claude (Anthropic) |

### Pipeline Flow
### Retrieval Layer (RAG)

- SEC filings chunked into 512-word segments with 50-word overlap
- Embedded with `sentence-transformers` (all-MiniLM-L6-v2)
- Stored in ChromaDB (local vector store, no cost)
- Hybrid retrieval: dense vector search + BM25 keyword search
- Results merged with Reciprocal Rank Fusion

---

## Key Results (Ablation Study — AAPL)

| Mode | Latency | Chunks Retrieved | Confidence Score |
|------|---------|-----------------|-----------------|
| Single agent (Analyst only) | 450ms | 0 | N/A |
| Full 4-agent pipeline | 18,804ms | 947 | 20% |

The full pipeline is 41.8x slower but retrieves 947 grounded chunks from the real SEC filing and produces a confidence score with critique flags — capabilities the single agent cannot provide.

---

## Project Structure
multi-agent-finance/
├── src/
│   ├── agents/          ← researcher, analyst, news_agent, critic
│   ├── graph/           ← LangGraph workflow
│   ├── retrieval/       ← embedder, ChromaDB, hybrid search
│   ├── schemas/         ← Pydantic models (AgentState, FinalReport)
│   ├── api/             ← FastAPI endpoints
│   └── dashboard/       ← Streamlit app
├── evaluation/          ← ablation study, hallucination rate
├── data/                ← cached filings (gitignored)
├── reports/             ← JSON audit trail per run
└── tests/               ← pytest test suite


---

## Quickstart

```bash
git clone https://github.com/Aminm-mgh/multi-agent-finance.git
cd multi-agent-finance
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # fill in your API keys
```

Start the API:
```bash
uvicorn src.api.main:app --reload
```

Start the dashboard (new terminal):
```bash
streamlit run src/dashboard/app.py
```

Run the ablation study:
```bash
PYTHONPATH=$(pwd) python evaluation/ablation.py
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyse` | Run full pipeline for a ticker |
| GET | `/report/{run_id}` | Retrieve stored report by ID |
| GET | `/health` | Health check |

Example:
```bash
curl -X POST http://localhost:8000/analyse \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "company_name": "Apple"}'
```

---

## Tech Stack

| Library | Purpose |
|---------|---------|
| `langgraph` | Agent orchestration state machine |
| `langchain-anthropic` | Claude integration |
| `chromadb` | Local vector store |
| `sentence-transformers` | Text embeddings |
| `rank-bm25` | Keyword search |
| `yfinance` | Live financial data |
| `pydantic v2` | Typed agent boundaries |
| `fastapi` | REST API |
| `streamlit` | Visual dashboard |

---

## Academic References

- Yao et al. (2023) — ReAct: Synergizing Reasoning and Acting in Language Models (ICLR 2023)
- Wu et al. (2023) — AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation (Microsoft Research)
- Lewis et al. (2020) — Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (NeurIPS 2020)
- QRT Labs (2026) — Imperial/Oxford/Cambridge joint initiative on agentic AI for financial systems