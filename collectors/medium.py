"""
Medium Scraper
- Medium 기술 관련 인기 글 수집
- Playwright 사용하여 동적 페이지 로딩
"""

import os
from typing import Optional

PLAYWRIGHT_AVAILABLE = False
sync_playwright = None

try:
    from playwright.sync_api import sync_playwright as _sync_playwright
    sync_playwright = _sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    pass


# ============================================================
# Medium 기술 관련 태그 목록
# ============================================================
# 사용 가능한 주요 기술 태그들:
#   - technology: 기술 전반 (가장 포괄적)
#   - programming: 프로그래밍 전반
#   - software-engineering: 소프트웨어 엔지니어링
#   - artificial-intelligence: AI/인공지능
#   - machine-learning: 머신러닝
#   - data-science: 데이터 사이언스
#   - devops: DevOps
#   - cloud-computing: 클라우드
#   - web-development: 웹 개발
#   - mobile-development: 모바일 개발
#   - cybersecurity: 보안
#   - python, javascript, etc.: 언어별 태그
#
# QA 관련 태그:
#   - software-testing: 소프트웨어 테스팅
#   - test-automation: 테스트 자동화
#   - quality-assurance: QA
#   - selenium, cypress: 테스트 도구
#
# 현재 사용 중인 태그: (여러 태그 순회하며 수집)
MEDIUM_TAGS = [
    "technology",
    "artificial-intelligence",
    "programming",
]
# ============================================================


def collect(limit: int = 10, session_id: Optional[str] = None) -> list[dict]:
    """
    Collect popular tech articles from Medium across multiple tags.

    Args:
        limit: Maximum number of articles to return (total, not per tag)
        session_id: Medium session ID for authenticated access (optional)

    Returns:
        List of article information dictionaries
    """
    if not PLAYWRIGHT_AVAILABLE or sync_playwright is None:
        print("[Medium] Playwright not installed. Run: pip install playwright && playwright install")
        return []

    session_id = session_id or os.getenv("MEDIUM_SESSION_ID")
    results = []
    seen_titles = set()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )

            # Set session cookie if provided (for paywalled content)
            if session_id:
                context.add_cookies([{
                    "name": "sid",
                    "value": session_id,
                    "domain": ".medium.com",
                    "path": "/",
                }])

            page = context.new_page()
            page.set_default_timeout(15000)

            # 여러 태그 순회하며 수집
            for tag in MEDIUM_TAGS:
                if len(results) >= limit:
                    break

                try:
                    tag_url = f"https://medium.com/tag/{tag}"
                    page.goto(tag_url, wait_until="commit")
                    page.wait_for_timeout(4000)  # Wait for JS rendering

                    # Find all h2 elements (article titles)
                    h2_elements = page.query_selector_all("h2")

                    for h2 in h2_elements:
                        if len(results) >= limit:
                            break

                        try:
                            title = h2.inner_text().strip()

                            # Skip non-article titles
                            if not title or len(title) < 15:
                                continue
                            if "Recommended" in title or "stories in" in title.lower():
                                continue

                            # Skip duplicates (across all tags)
                            if title in seen_titles:
                                continue
                            seen_titles.add(title)

                            # Get parent link using JavaScript
                            href = h2.evaluate("el => { const a = el.closest('a'); return a ? a.href : ''; }")

                            # Make absolute URL
                            if href and href.startswith("/"):
                                href = f"https://medium.com{href}"

                            # Clean URL
                            if href and "?" in href:
                                href = href.split("?")[0]

                            results.append({
                                "source": "Medium",
                                "title": title,
                                "url": href or "",
                                "summary": "",
                                "tag": tag,
                            })

                        except Exception:
                            continue

                except Exception as e:
                    print(f"[Medium] Error fetching tag '{tag}': {e}")
                    continue

            browser.close()

    except Exception as e:
        print(f"[Medium] Browser error: {e}")
        return []

    return results


if __name__ == "__main__":
    print("Fetching Medium tech articles...\n")
    print(f"Tags: {', '.join(MEDIUM_TAGS)}\n")
    print("Note: For full access to paywalled content, set MEDIUM_SESSION_ID\n")

    articles = collect(limit=10)
    print(f"Found {len(articles)} articles\n")
    for i, a in enumerate(articles, 1):
        title_display = a['title'][:60] + "..." if len(a['title']) > 60 else a['title']
        print(f"{i}. [{a.get('tag', '')}] {title_display}")
        if a['url']:
            print(f"   URL: {a['url']}")
        print()
