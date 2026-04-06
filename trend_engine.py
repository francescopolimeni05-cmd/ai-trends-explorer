import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from data_loader import embed_texts
from qdrant_client import QdrantClient

load_dotenv()

TREND_TOPICS = [
    "Large language models and foundation models",
    "AI agents and autonomous systems",
    "Multimodal AI and vision-language models",
    "AI safety, alignment, and interpretability",
    "Efficient AI: quantization, distillation, edge deployment",
    "Retrieval-augmented generation and knowledge systems",
    "AI applications in science, biology, and medicine",
]

def _openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=api_key)

def _qdrant_client() -> QdrantClient:
    return QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))

def _strip_links(text: str) -> str:
    """Remove markdown links, bare URLs, and parenthetical domain citations from answer text."""
    # Remove markdown links [text](url) → text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove bare URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove parenthetical domain references like (ibm.com) or (arxiv.org)
    text = re.sub(r'\([a-zA-Z0-9\-]+\.[a-zA-Z]{2,}[^\)]*\)', '', text)
    # Remove leftover empty parentheses
    text = re.sub(r'\(\s*\)', '', text)
    # Clean up extra spaces before punctuation
    text = re.sub(r'\s+([.,;:])', r'\1', text)
    # Clean up multiple spaces
    text = re.sub(r'  +', ' ', text)
    return text.strip()

def retrieve_signals_for_topic(topic: str, top_k: int = 6) -> list[dict]:
    """Query Qdrant for the most relevant items about a given topic."""
    query_vector = embed_texts([topic])[0]
    hits = _qdrant_client().query_points(
        collection_name="documents",
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points
    return [hit.payload for hit in hits]

def synthesize_topic(topic: str, signals: list[dict]) -> dict:
    """Generate a synthesis paragraph for a topic given retrieved signals."""
    if not signals:
        return {
            "topic": topic,
            "summary": "No signals found.",
            "key_signals": [],
            "signal_count": 0,
        }

    context_lines = []
    for s in signals:
        snippet = s.get("text", "")[:400]
        context_lines.append(
            f"[{s.get('source_type','').upper()} | {s.get('date','')}] "
            f"{s.get('title','')}\n{snippet}"
        )
    context_block = "\n---\n".join(context_lines)

    prompt = f"""You are an AI research analyst for a consulting firm.
Analyze the following recent signals about the topic: "{topic}"

SIGNALS:
{context_block}

Write a 3-4 sentence synthesis covering:
1. What is the main direction of progress in this area right now?
2. What is the most salient recent development?
3. What should a decision-maker pay attention to?

Be specific, cite titles when relevant, and avoid generic statements.
Write in professional prose. Do not use bullet points. Do not include URLs or links."""

    response = _openai_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a concise, insightful AI research analyst. Never include URLs or hyperlinks in your responses."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=300,
        temperature=0.3,
    )

    key_signals = [
        {
            "title": s.get("title", "")[:80],
            "url": s.get("url", ""),
            "source": s.get("source_type", ""),
            "date": s.get("date", ""),
        }
        for s in signals[:3]
    ]

    return {
        "topic": topic,
        "summary": _strip_links(response.choices[0].message.content.strip()),
        "key_signals": key_signals,
        "signal_count": len(signals),
    }

def get_all_trends() -> list[dict]:
    """Main entry point — returns synthesized trend cards for all topics."""
    trends = []
    for topic in TREND_TOPICS:
        print(f"[trend_engine] Synthesizing: {topic[:50]}...")
        signals = retrieve_signals_for_topic(topic, top_k=6)
        trends.append(synthesize_topic(topic, signals))
    return trends

def generate_weekly_digest() -> str:
    """Generates a full narrative weekly briefing across all topics."""
    all_signals = []
    for topic in TREND_TOPICS[:4]:
        all_signals.extend(retrieve_signals_for_topic(topic, top_k=4))

    seen, unique = set(), []
    for s in all_signals:
        if s.get("title") not in seen:
            seen.add(s.get("title"))
            unique.append(s)

    context_block = "\n".join(
        f"- [{s.get('source_type','').upper()} | {s.get('date','')}] {s.get('title','')}"
        for s in unique[:20]
    )

    prompt = f"""You are writing the weekly AI briefing for a consulting firm's leadership team.

Based on these recent signals:
{context_block}

Write a structured weekly digest with:
1. **Executive Summary** (2-3 sentences on the most important development this week)
2. **Top 3 Trends to Watch** (each with a 2-sentence explanation)
3. **Signals for Decision Makers** (2-3 practical implications for strategy or investment)

Use markdown formatting. Be specific and analytical.
Do not include any URLs or hyperlinks in the text."""

    response = _openai_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a senior AI research analyst writing for executives. Never include URLs or hyperlinks in your responses."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=800,
        temperature=0.3,
    )
    return _strip_links(response.choices[0].message.content.strip())

def answer_question(question: str, top_k: int = 6) -> dict:
    query_vector = embed_texts([question])[0]
    hits = _qdrant_client().query_points(
        collection_name="documents",
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points

    client = _openai_client()

    context_block = "\n\n".join(
        f"[{h.payload.get('source_type','').upper()} | {h.payload.get('date','')}] "
        f"{h.payload.get('title','')}\n{h.payload.get('text','')[:400]}"
        for h in hits
    ) if hits else ""

    web_sources = []
    answer = ""
    used_web = False

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            tools=[{"type": "web_search_preview"}],
            tool_choice={"type": "web_search_preview"},
            instructions=(
                "You are a senior AI research analyst writing for a consulting firm. "
                "Answer in professional prose — no bullet spam, no URLs, no hyperlinks in the text. "
                "You have access to a curated knowledge base (provided as context) AND live web search. "
                "Use both. Prioritize the knowledge base when relevant, supplement with web for recent events. "
                "Never fabricate citations. Be precise and analytical."
            ),
            input=(
                f"Knowledge base context:\n{context_block}\n\n"
                f"Question: {question}\n\n"
                "Answer professionally in prose using both the knowledge base and web search. "
                "Do not include any URLs, links, or parenthetical references in your answer text."
            ),
        )

        # Extract answer text
        for block in response.output:
            if hasattr(block, "content") and isinstance(block.content, list):
                for content in block.content:
                    if hasattr(content, "text"):
                        answer += content.text
            elif hasattr(block, "text") and isinstance(block.text, str):
                answer += block.text

        # Detect web search usage from block types
        block_types = [type(block).__name__ for block in response.output]
        print(f"[trend_engine] block types: {block_types}")

        # Web was used if any non-message block appeared
        used_web = any(
            "Search" in t or "Tool" in t or t == "WebSearchToolCall"
            for t in block_types
        )

        # Also check via type attribute
        for block in response.output:
            if hasattr(block, "type"):
                t = str(getattr(block, "type", "")).lower()
                if "search" in t or "tool" in t:
                    used_web = True

        # Try structured annotation extraction
        for block in response.output:
            if hasattr(block, "content") and isinstance(block.content, list):
                for content in block.content:
                    if hasattr(content, "annotations") and content.annotations:
                        for ann in content.annotations:
                            if hasattr(ann, "url") and hasattr(ann, "title"):
                                web_sources.append({
                                    "title": ann.title[:80] if ann.title else ann.url,
                                    "url": ann.url,
                                })
                                used_web = True

        print(f"[trend_engine] used_web={used_web}, web_sources={len(web_sources)}, answer_len={len(answer)}")

    except Exception as e:
        print(f"[trend_engine] Responses API error: {e}")

    # Fallback to chat completions if Responses API failed or returned nothing
    if not answer:
        fallback = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    "You are a senior AI research analyst writing for a consulting firm. "
                    "Answer in professional prose. No URLs or hyperlinks in the text. "
                    "Trust the provided context. If context is insufficient, "
                    "answer from your own knowledge and say so explicitly."
                )},
                {"role": "user", "content": (
                    f"Context:\n{context_block}\n\nQuestion: {question}"
                )},
            ],
            max_tokens=600,
            temperature=0.3,
        )
        answer = fallback.choices[0].message.content.strip()
        used_web = False

    kb_sources = [
        {
            "title": h.payload.get("title", "")[:80],
            "url": h.payload.get("url", ""),
            "source": h.payload.get("source_type", ""),
            "date": h.payload.get("date", ""),
        }
        for h in hits
    ]

    clean_answer = _strip_links(answer) or "No answer could be generated."

    return {
        "answer": clean_answer,
        "kb_sources": kb_sources,
        "web_sources": web_sources,
        "used_web": used_web,
    }