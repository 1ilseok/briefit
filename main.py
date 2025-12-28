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

    print(f"📝 Summarizing {len(news)} items...")
    summary = summarize(news)

    print("📧 Sending email...")
    send(summary)

    print("✅ Done!")


if __name__ == "__main__":
    main()
