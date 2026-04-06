from dotenv import load_dotenv
load_dotenv()
from trend_engine import retrieve_signals_for_topic

topics = [
    "Large language models and foundation models",
    "AI safety, alignment, and interpretability",
]
for topic in topics:
    signals = retrieve_signals_for_topic(topic, top_k=3)
    print(f"\nTopic: {topic[:50]}")
    for s in signals:
        print(f"  - {s.get('title','')[:60]}")