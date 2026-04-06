import json
from pathlib import Path
from datetime import datetime

HISTORY_FILE = Path("qa_history.json")

def save_qa(question: str, answer: str, kb_sources: list, web_sources: list):
    history = load_history()
    history.insert(0, {
        "question": question,
        "answer": answer,
        "kb_sources": kb_sources,
        "web_sources": web_sources,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "date": datetime.now().strftime("%B %d, %Y"),
        "week": datetime.now().isocalendar()[1],
    })
    # Keep last 50
    history = history[:50]
    HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False))

def load_history() -> list:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text())
    except Exception:
        return []