"""
Hacker News API Collector
- Algolia HN Search API를 사용하여 최근 N일간 베스트 스토리 수집
"""

import requests
from datetime import datetime, timedelta, timezone


ALGOLIA_HN_API = "https://hn.algolia.com/api/v1/search"


def get_date_range(days: int = 7) -> tuple[datetime, datetime]:
    """
    Get the date range for the past N days.

    Args:
        days: Number of days to look back

    Returns:
        Tuple of (start_date, end_date) in UTC
    """
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)

    return start_date, now


def collect(days: int = 7, limit: int = 20) -> list[dict]:
    """
    Collect top stories from Hacker News for the past N days.

    Args:
        days: Number of days to look back (default: 7)
        limit: Maximum number of stories to return (default: 20)

    Returns:
        List of story information dictionaries sorted by score
    """
    start_date, end_date = get_date_range(days)

    # Convert to Unix timestamps
    start_ts = int(start_date.timestamp())
    end_ts = int(end_date.timestamp())

    try:
        # search API sorts by points (relevance) by default
        response = requests.get(
            ALGOLIA_HN_API,
            params={
                "tags": "story",
                "numericFilters": f"created_at_i>={start_ts},created_at_i<={end_ts}",
                "hitsPerPage": limit,
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"[HackerNews] Error fetching stories: {e}")
        return []

    results = []
    for hit in data.get("hits", []):
        results.append({
            "source": "Hacker News",
            "title": hit.get("title"),
            "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
            "score": hit.get("points"),
            "comments": hit.get("num_comments", 0),
            "hn_url": f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
            "created_at": hit.get("created_at"),
        })

    # Sort by score descending
    results.sort(key=lambda x: x.get("score", 0), reverse=True)

    return results


if __name__ == "__main__":
    # Test the collector
    start, end = get_date_range(days=7)
    print(f"Fetching top 20 stories from {start.date()} to {end.date()}\n")

    stories = collect(days=7, limit=20)
    print(f"Found {len(stories)} stories\n")
    for s in stories:
        print(f"[{s['score']}pts] {s['title']}")
        print(f"  URL: {s['url']}")
        print(f"  Comments: {s['comments']}")
        print()
