"""
seed_db.py
Run once to populate Qdrant with arXiv papers + RSS articles.
Usage: uv run python seed_db.py
"""
import uuid
from dotenv import load_dotenv
from data_loader import embed_texts
from vector_db import QdrantStorage
from ingestion.arxiv_fetcher import fetch_arxiv_papers
from ingestion.news_fetcher import fetch_rss_articles

load_dotenv()

def seed():
    print("=== AI Trends Explorer — Seeding Qdrant ===\n")
    db = QdrantStorage()

    all_items = []
    all_items.extend(fetch_arxiv_papers(max_results_per_category=15))
    all_items.extend(fetch_rss_articles(max_per_feed=10))

    print(f"\nTotal items to embed and store: {len(all_items)}")
    print("Generating embeddings (this takes ~1-2 min)...\n")

    texts = [item["text"] for item in all_items]
    vectors = embed_texts(texts)

    ids = []
    payloads = []
    for i, item in enumerate(all_items):
        uid = str(uuid.uuid5(uuid.NAMESPACE_URL, item["url"] or f"item-{i}"))
        ids.append(uid)
        payloads.append({
            "text": item["text"],
            "title": item["title"],
            "url": item["url"],
            "date": item["date"],
            "source_type": item["source_type"],
            "category": item.get("category", ""),
            "feed_name": item.get("feed_name", "arXiv"),
        })

    db.upsert(ids, vectors, payloads)
    print(f"\n✓ Successfully stored {len(ids)} items in Qdrant.")
    print("You can now run: uv run streamlit run streamlit_app.py")

if __name__ == "__main__":
    seed()