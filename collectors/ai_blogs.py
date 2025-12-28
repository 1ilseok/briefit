"""
AI Blogs Collector
- OpenAI Blog (RSS) + Anthropic News (웹 스크래핑)에서 최신 글 수집
"""

import requests
import xml.etree.ElementTree as ET
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from typing import Optional


OPENAI_RSS_URL = "https://openai.com/blog/rss.xml"
ANTHROPIC_NEWS_URL = "https://www.anthropic.com/news"


def parse_rss_date(date_str: str) -> Optional[datetime]:
    """Parse RSS date format to datetime."""
    formats = [
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def fetch_rss(url: str, source_name: str, days: int = 7, limit: int = 5) -> list[dict]:
    """
    Fetch articles from an RSS feed.

    Args:
        url: RSS feed URL
        source_name: Name of the source (e.g., "OpenAI", "Anthropic")
        days: Only include articles from the last N days
        limit: Maximum number of articles to return

    Returns:
        List of article information dictionaries
    """
    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            },
            timeout=10
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[{source_name}] Error fetching RSS: {e}")
        return []

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"[{source_name}] Error parsing RSS: {e}")
        return []

    # Handle both RSS 2.0 and Atom formats
    items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    results = []

    for item in items:
        if len(results) >= limit:
            break

        # RSS 2.0 format
        title = item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title")
        link = item.findtext("link") or ""
        if not link:
            link_elem = item.find("{http://www.w3.org/2005/Atom}link")
            if link_elem is not None:
                link = link_elem.get("href", "")

        pub_date_str = item.findtext("pubDate") or item.findtext("{http://www.w3.org/2005/Atom}published")
        description = item.findtext("description") or item.findtext("{http://www.w3.org/2005/Atom}summary") or ""

        if not title or not link:
            continue

        # Parse and filter by date
        pub_date = parse_rss_date(pub_date_str) if pub_date_str else None
        if pub_date:
            # Make timezone-aware if not already
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=timezone.utc)
            if pub_date < cutoff_date:
                continue

        results.append({
            "source": source_name,
            "title": title.strip(),
            "url": link.strip(),
            "published_at": pub_date_str,
            "summary": description[:500] if description else "",
        })

    return results


def fetch_anthropic(days: int = 7, limit: int = 5) -> list[dict]:
    """
    Fetch articles from Anthropic News page via web scraping.

    Args:
        days: Only include articles from the last N days
        limit: Maximum number of articles to return

    Returns:
        List of article information dictionaries
    """
    try:
        response = requests.get(
            ANTHROPIC_NEWS_URL,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            },
            timeout=10
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[Anthropic] Error fetching page: {e}")
        return []

    soup = BeautifulSoup(response.text, "lxml")
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    results = []

    # Find article links - Anthropic uses /news/ paths
    for link in soup.find_all("a", href=re.compile(r"^/news/[^/]+$")):
        if len(results) >= limit:
            break

        href = link.get("href", "")
        url = f"https://www.anthropic.com{href}"

        # Get title
        title = link.get_text(strip=True)
        if not title or len(title) < 5:
            # Try to find title in nested elements
            h_tag = link.find(["h1", "h2", "h3", "h4"])
            if h_tag:
                title = h_tag.get_text(strip=True)

        if not title or len(title) < 5:
            continue

        # Skip duplicates
        if any(r["url"] == url for r in results):
            continue

        results.append({
            "source": "Anthropic",
            "title": title,
            "url": url,
            "published_at": None,
            "summary": "",
        })

    return results


def collect(days: int = 7, limit_per_source: int = 5) -> list[dict]:
    """
    Collect articles from OpenAI and Anthropic blogs.

    Args:
        days: Only include articles from the last N days
        limit_per_source: Maximum number of articles per source

    Returns:
        List of article information dictionaries
    """
    results = []

    # OpenAI Blog (RSS)
    results.extend(fetch_rss(OPENAI_RSS_URL, "OpenAI", days, limit_per_source))

    # Anthropic News (Web scraping)
    results.extend(fetch_anthropic(days, limit_per_source))

    return results


if __name__ == "__main__":
    # Test the collector (30 days for testing)
    print("Fetching AI blog articles (last 30 days)...\n")
    articles = collect(days=30, limit_per_source=5)
    print(f"Found {len(articles)} articles\n")
    for a in articles:
        print(f"[{a['source']}] {a['title']}")
        print(f"  URL: {a['url']}")
        print(f"  Date: {a['published_at']}")
        print()
