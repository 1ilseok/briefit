"""
TLDR Newsletter Scraper
- tldr.tech에서 최신 뉴스레터 기사 수집
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re


def get_latest_newsletter_url() -> str:
    """Get the URL for the latest TLDR newsletter."""
    today = datetime.now()
    # Try today first, then go back up to 3 days
    for days_back in range(4):
        date = today - timedelta(days=days_back)
        # Skip weekends (TLDR doesn't publish on weekends)
        if date.weekday() >= 5:
            continue
        date_str = date.strftime("%Y-%m-%d")
        return f"https://tldr.tech/tech/{date_str}"
    return "https://tldr.tech/tech"


def collect(limit: int = 10) -> list[dict]:
    """
    Collect articles from TLDR Tech newsletter.

    Args:
        limit: Maximum number of articles to return (default: 10)

    Returns:
        List of article information dictionaries
    """
    url = get_latest_newsletter_url()

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
        print(f"[TLDR] Error fetching page: {e}")
        return []

    soup = BeautifulSoup(response.text, "lxml")
    results = []

    # Find all article links with utm_source (external article links)
    article_links = soup.find_all("a", href=re.compile(r"utm_source=tldr"))

    seen_urls = set()
    for link in article_links:
        href = link.get("href", "")

        # Skip if already seen
        if href in seen_urls:
            continue
        seen_urls.add(href)

        # Get title from h3 tag or link text
        h3 = link.find("h3")
        if h3:
            title = h3.get_text(strip=True)
        else:
            title = link.get_text(strip=True)

        if not title or len(title) < 10:
            continue

        # Skip sponsor/ad content
        if "(Sponsor)" in title or "tldr.tech" in href:
            continue

        # Clean up title (remove read time pattern like "(3 minute read)")
        title = re.sub(r"\s*\(\d+\s*minute\s*read\)\s*", "", title).strip()

        # Get summary from p tag if available
        summary = ""
        p_tag = link.find("p")
        if p_tag:
            summary = p_tag.get_text(strip=True)

        results.append({
            "source": "TLDR",
            "title": title,
            "url": href.split("?")[0],  # Remove utm params for clean URL
            "summary": summary,
        })

        if len(results) >= limit:
            break

    return results


if __name__ == "__main__":
    # Test the collector
    print(f"Fetching from: {get_latest_newsletter_url()}\n")
    articles = collect(limit=10)
    print(f"Found {len(articles)} articles\n")
    for a in articles:
        title_display = a['title'][:70] + "..." if len(a['title']) > 70 else a['title']
        print(f"• {title_display}")
        print(f"  URL: {a['url']}")
        if a.get('summary'):
            summary_display = a['summary'][:100] + "..." if len(a['summary']) > 100 else a['summary']
            print(f"  Summary: {summary_display}")
        print()
