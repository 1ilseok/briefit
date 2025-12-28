"""
Playwright GitHub Releases Collector
"""

import requests
from datetime import datetime, timedelta, timezone
from typing import Optional


GITHUB_API_URL = "https://api.github.com/repos/microsoft/playwright/releases"


def collect(days: int = 7, limit: int = 5) -> list[dict]:
    """
    Collect recent Playwright releases from GitHub.

    Args:
        days: Only include releases from the last N days
        limit: Maximum number of releases to return

    Returns:
        List of release information dictionaries
    """
    try:
        response = requests.get(
            GITHUB_API_URL,
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=10
        )
        response.raise_for_status()
        releases = response.json()
    except requests.RequestException as e:
        print(f"[Playwright] Error fetching releases: {e}")
        return []

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    results = []

    for release in releases[:limit]:
        published_at = parse_date(release.get("published_at"))

        if published_at and published_at < cutoff_date:
            continue

        results.append({
            "source": "Playwright",
            "title": release.get("name") or release.get("tag_name"),
            "url": release.get("html_url"),
            "published_at": release.get("published_at"),
            "body": release.get("body", "")[:1000],  # Limit body length
            "tag": release.get("tag_name"),
        })

    return results


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse GitHub date string to datetime."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError:
        return None


if __name__ == "__main__":
    # Test the collector (90 days for testing)
    releases = collect(days=90)
    print(f"Found {len(releases)} releases")
    for r in releases:
        print(f"[{r['tag']}] {r['title']}")
        print(f"  URL: {r['url']}")
        print(f"  Published: {r['published_at']}")
        print()
