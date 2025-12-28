"""
Briefit - AI-powered IT news briefing service
"""

from collectors import playwright_releases, hackernews, tldr, ai_blogs, medium
from summarizer import openai_summarizer
from sender import email


def collect_all():
    """Collect news from all sources."""
    news = []

    # Playwright releases
    news.extend(playwright_releases.collect())

    # Hacker News top stories
    news.extend(hackernews.collect())

    # TLDR newsletter
    news.extend(tldr.collect())

    # AI blogs (OpenAI + Anthropic)
    news.extend(ai_blogs.collect())

    # Medium articles
    news.extend(medium.collect())

    return news


def summarize(news: list) -> str:
    """Summarize collected news using OpenAI."""
    return openai_summarizer.summarize(news)


def send(content: str):
    """Send email to team."""
    email.send(content)


def main():
    print("📡 Collecting news...")
    news = collect_all()

    # 디버깅: 소스별 수집 개수 출력
    print("\n=== 수집 결과 ===")
    source_counts = {}
    for item in news:
        source = item.get("source", "Unknown")
        source_counts[source] = source_counts.get(source, 0) + 1
    for source, count in source_counts.items():
        print(f"  {source}: {count}개")
    print(f"  총합: {len(news)}개")
    print("=================\n")

    print(f"📝 Summarizing {len(news)} items...")
    summary = summarize(news)

    print("📧 Sending email...")
    send(summary)

    print("✅ Done!")


if __name__ == "__main__":
    main()
