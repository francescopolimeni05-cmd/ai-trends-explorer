# AI Trends Explorer

A consulting intelligence tool that automatically aggregates signals from AI research papers, news feeds, and uploaded reports — and synthesizes them into actionable briefings for decision makers.

Built for the course **Prototyping Products with Data and Artificial Intelligence** at ESADE Business School.

**Team:** Marc Sardà · Amat Montoto · Francesco Polimeni · Matteo Guardamagna

---

## What it does

Tracking developments in artificial intelligence across research, industry, and media is a manual, fragmented process. AI Trends Explorer automates ingestion from multiple sources and surfaces coherent signals through three interfaces:

- **Dashboard** — seven synthesized trend cards covering the most active areas in AI, each grounded in retrieved papers and articles from the current week
- **Weekly Digest** — a structured narrative briefing formatted for leadership, with executive summary, top trends, and strategic implications
- **Explorer** — semantic Q&A over the full knowledge base with source citations
- **Upload** — ingest proprietary PDF reports to extend the knowledge base

---

## System architecture
```
Sources                  Ingestion              Storage         Intelligence
──────────────────────   ────────────────────   ─────────────   ─────────────────────
arXiv (cs.AI, cs.LG,  →  fetch + chunk +     →  Qdrant        →  GPT-4o-mini
cs.CL, stat.ML)          embed (OpenAI            vector           synthesis per topic
                         text-embedding-          store            + weekly digest
RSS feeds                3-large, 3072-dim)       (COSINE          + Q&A with
(VentureBeat,                                     similarity)      source attribution
MIT TR, The Gradient,    Inngest async
Google Research,         orchestration
OpenAI News)             for PDF uploads

PDF reports
(manual upload)
```

**Stack:** Python 3.13 · FastAPI · Inngest · Qdrant · OpenAI · Streamlit · LlamaIndex · RAGAS

---

## Performance

| Metric | Score |
|---|---|
| Faithfulness (RAGAS) | 94.3% |
| Answer Relevancy (RAGAS) | 73.6% |
| Query latency | ~7s avg |
| Knowledge base | ~100 items (arXiv + RSS) |

---

## Setup

### Prerequisites

- Python 3.13+
- Docker (for Qdrant)
- OpenAI API key
- Node.js (for Inngest CLI)

### Installation
```bash
git clone https://github.com/msardamasri/ai-trends-explorer.git
cd ai-trends-explorer
pip install uv
uv sync
```

Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your-key-here
QDRANT_URL=http://localhost:6333
INNGEST_API_BASE=http://127.0.0.1:8288/v1
```

### Run

**First time only — seed the knowledge base:**
```bash
# Step 1 — Start Qdrant with persistent storage
docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant

# Step 2 — Seed Qdrant with arXiv papers + RSS articles (~2 min)
uv run python seed_db.py
```

**Every time — start all services:**
```bash
# Terminal 1 — Qdrant with persistent storage (keep running)
docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant

# Terminal 2 — FastAPI + Inngest functions (required for PDF upload)
uv run uvicorn main:app --reload

# Terminal 3 — Inngest dev server (required for PDF upload)
npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery

# Terminal 4 — Streamlit
uv run streamlit run streamlit_app.py
```

Open [http://localhost:8501](http://localhost:8501).

**Note:** Terminals 2 and 3 are only required if you want to use the PDF upload feature. For the dashboard, digest, and explorer, only Terminal 1 and Terminal 4 are needed.

---

## Project structure
```
ai-trends-explorer/
├── ingestion/
│   ├── arxiv_fetcher.py       arXiv paper retrieval (cs.AI, cs.LG, cs.CL, stat.ML)
│   └── news_fetcher.py        RSS feed ingestion (5 curated sources)
├── pages/
│   ├── dashboard.py           Trend cards page
│   ├── digest.py              Weekly digest page
│   ├── explorer.py            Semantic Q&A page
│   └── upload.py              PDF ingestion page
├── trend_engine.py            Retrieval + GPT-4o-mini synthesis layer
├── seed_db.py                 One-shot knowledge base population script
├── styles.py                  Shared CSS injection + sidebar navigation
├── streamlit_app.py           Home page
├── main.py                    FastAPI app with Inngest functions
├── vector_db.py               Qdrant interface
├── data_loader.py             PDF processing and embedding
└── evaluate_rag.py            RAGAS evaluation script
```

---

## Sources

| Source | Type | Category |
|---|---|---|
| arXiv cs.AI | Research papers | Artificial Intelligence |
| arXiv cs.LG | Research papers | Machine Learning |
| arXiv cs.CL | Research papers | Computation and Language |
| arXiv stat.ML | Research papers | Statistical ML |
| VentureBeat AI | News | Industry |
| MIT Technology Review | News | Research + Industry |
| The Gradient | Articles | Research |
| Google Research Blog | Articles | Research |
| OpenAI News | News | Industry |

---

## License

MIT