"""
TLDR Newsletter Scraper
- tldr.tech에서 최근 7일간 뉴스레터 기사 수집
- 날짜별 상위 3개씩 (편집팀 배치 순서 기준)
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re


def get_newsletter_urls(days: int = 7) -> list[tuple[str, str]]:
    """
    Get URLs for TLDR newsletters for the past N days.

    Args:
        days: Number of days to look back

    Returns:
        List of (url, date_str) tuples for valid weekdays
    """
    urls = []
    today = datetime.now()

    for days_back in range(days + 7):  # Extra buffer for weekends
        if len(urls) >= days:
            break

        date = today - timedelta(days=days_back)
        # Skip weekends (TLDR doesn't publish on weekends)
        if date.weekday() >= 5:
            continue

        date_str = date.strftime("%Y-%m-%d")
        urls.append((f"https://tldr.tech/tech/{date_str}", date_str))

    return urls[:days]


def fetch_articles_from_page(url: str, date_str: str, limit: int = 3) -> list[dict]:
    """
    Fetch top articles from a single TLDR newsletter page.

    Args:
        url: Newsletter URL
        date_str: Date string for the newsletter
        limit: Maximum number of articles to return from this page

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
        print(f"[TLDR] Error fetching {date_str}: {e}")
        return []

    soup = BeautifulSoup(response.text, "lxml")
    results = []

    # Find all article links with utm_source (external article links)
    article_links = soup.find_all("a", href=re.compile(r"utm_source=tldr"))

    seen_urls = set()
    for link in article_links:
        if len(results) >= limit:
            break

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
            "date": date_str,
        })

    return results


def collect(days: int = 7, per_day: int = 3) -> list[dict]:
    """
    Collect top articles from TLDR Tech newsletters for the past N days.

    Args:
        days: Number of days to look back (default: 7)
        per_day: Number of top articles per day (default: 3)

    Returns:
        List of article information dictionaries
    """
    urls = get_newsletter_urls(days)
    results = []
    seen_urls = set()

    for url, date_str in urls:
        articles = fetch_articles_from_page(url, date_str, per_day)

        for article in articles:
            # Skip duplicates across days
            if article["url"] in seen_urls:
                continue
            seen_urls.add(article["url"])
            results.append(article)

    return results


if __name__ == "__main__":
    # Test the collector
    print("Fetching TLDR articles (last 7 days, top 3 per day)...\n")
    articles = collect(days=7, per_day=3)
    print(f"Found {len(articles)} articles\n")

    current_date = None
    for a in articles:
        if a.get('date') != current_date:
            current_date = a.get('date')
            print(f"\n=== {current_date} ===")

        title_display = a['title'][:70] + "..." if len(a['title']) > 70 else a['title']
        print(f"• {title_display}")
        print(f"  URL: {a['url']}")
        if a.get('summary'):
            summary_display = a['summary'][:100] + "..." if len(a['summary']) > 100 else a['summary']
            print(f"  Summary: {summary_display}")
