import arxiv
from datetime import datetime

ARXIV_CATEGORIES = [
    "cs.AI",
    "cs.LG",
    "cs.CL",
    "stat.ML",
    "q-bio.QM",
]

def fetch_arxiv_papers(max_results_per_category: int = 10) -> list[dict]:
    """
    Fetch recent papers from arXiv across AI/ML categories.
    Returns list of dicts with keys: text, title, url, date, source_type, category.
    """
    client = arxiv.Client()
    papers = []
    seen_ids = set()

    for category in ARXIV_CATEGORIES:
        print(f"[arXiv] Fetching category: {category}...")
        search = arxiv.Search(
            query=f"cat:{category}",
            max_results=max_results_per_category,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )
        for result in client.results(search):
            if result.entry_id in seen_ids:
                continue
            seen_ids.add(result.entry_id)

            text = f"TITLE: {result.title}\n\nABSTRACT: {result.summary}"

            papers.append({
                "text": text,
                "title": result.title,
                "url": result.entry_id,
                "date": result.published.strftime("%Y-%m-%d"),
                "source_type": "arxiv",
                "category": category,
                "feed_name": "arXiv",
            })

    print(f"[arXiv] Done. Fetched {len(papers)} papers total.")
    return papers