import re
import feedparser
from utils.db import add_paper, get_latest_papers
from typing import Any

FEED_URLS: list[str] = [
    "https://arxiv.org/rss/cs.AI",
    "https://arxiv.org/rss/cs.LG",
    "https://arxiv.org/rss/cs.CL",
]


async def get_arxiv_id(url: str):
    return url.split("/")[-1]


async def parse_authors(authors_field: Any | None) -> str:

    if not authors_field:
        return ""

    first = authors_field[0]
    if isinstance(first, dict) and "name" in first:
        return first["name"].strip()
    if hasattr(first, "name"):
        return first.name.strip()
    if isinstance(first, str):
        return first.strip()

    return ""


def clean_summary(summary: str) -> str:
    """Remove arXiv metadata prefix from summary text."""
    if not summary:
        return ""

    cleaned = re.sub(
        r"^arXiv:\S+\s+Announce Type:\s+\w+\s*\n?Abstract:\s*",
        "",
        summary,
        flags=re.IGNORECASE,
    )
    return cleaned.strip()


async def update_papers(feed_urls: list[str] = FEED_URLS, limit: int = 10):
    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:limit]:
            paper = {
                "arxiv_id": await get_arxiv_id(entry.link),
                "title": entry.title,
                "link": entry.link,
                "summary": clean_summary(entry.get("summary", "")),
                "authors": await parse_authors(entry.get("authors", "")),
                "published": entry.get("published", ""),
                "category": url.split("/")[-1],
            }

            await add_paper(paper)
    return await get_latest_papers(limit)
