"""
OpenAI Summarizer
- 수집된 뉴스를 OpenAI API를 사용하여 한국어로 요약
"""

import os
from openai import OpenAI


def summarize(news: list[dict]) -> str:
    """
    Summarize collected news using OpenAI API.

    Args:
        news: List of news items from various sources

    Returns:
        Formatted summary in Korean (HTML format for email)
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[Summarizer] OPENAI_API_KEY not set")
        return _format_without_summary(news)

    client = OpenAI(api_key=api_key)

    # Group news by source
    grouped = {}
    for item in news:
        source = item.get("source", "Other")
        if source not in grouped:
            grouped[source] = []
        grouped[source].append(item)

    # Create prompt for summarization
    prompt = _build_prompt(grouped)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """당신은 IT 뉴스 큐레이터입니다.
주어진 뉴스 목록을 분석하여 QA 엔지니어/개발자 팀에게 유용한 주간 브리핑을 작성합니다.

작성 규칙:
1. 한국어로 작성
2. 각 소스별로 주요 내용 요약
3. 기술적 인사이트와 팀에 적용 가능한 포인트 강조
4. 간결하면서도 핵심을 담아 작성
5. HTML 형식으로 출력 (이메일용)
6. 이모지 적절히 사용하여 가독성 향상
7. 제공된 모든 기사를 빠짐없이 포함할 것 (생략 금지)
8. 각 소스 내에서 화제성과 중요도를 고려하여 순서를 정렬할 것"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=4000,
            temperature=0.7,
        )

        summary = response.choices[0].message.content
        return summary

    except Exception as e:
        print(f"[Summarizer] OpenAI API error: {e}")
        return _format_without_summary(news)


def _build_prompt(grouped: dict) -> str:
    """Build the prompt for OpenAI from grouped news items."""
    lines = ["아래 뉴스들을 분석하여 주간 IT 브리핑을 작성해주세요:\n"]

    source_order = [
        "Playwright",
        "Hacker News",
        "TLDR",
        "OpenAI",
        "Anthropic",
        "Medium",
    ]

    # Process in preferred order
    for source in source_order:
        if source not in grouped:
            continue

        items = grouped[source]
        lines.append(f"\n## {source} ({len(items)}개)")

        for item in items:
            title = item.get("title", "")
            url = item.get("url", "")
            summary = item.get("summary", "")

            lines.append(f"- 제목: {title}")
            if url:
                lines.append(f"  URL: {url}")
            if summary:
                lines.append(f"  요약: {summary[:200]}")

    # Process remaining sources
    for source, items in grouped.items():
        if source in source_order:
            continue

        lines.append(f"\n## {source} ({len(items)}개)")
        for item in items:
            title = item.get("title", "")
            url = item.get("url", "")
            lines.append(f"- 제목: {title}")
            if url:
                lines.append(f"  URL: {url}")

    return "\n".join(lines)


def _format_without_summary(news: list[dict]) -> str:
    """Format news as simple HTML list without AI summary."""
    html_parts = [
        "<html><body>",
        "<h1>📡 Weekly IT Briefing</h1>",
        "<p><em>AI 요약을 사용할 수 없어 원본 목록을 제공합니다.</em></p>",
    ]

    # Group by source
    grouped = {}
    for item in news:
        source = item.get("source", "Other")
        if source not in grouped:
            grouped[source] = []
        grouped[source].append(item)

    for source, items in grouped.items():
        html_parts.append(f"<h2>{source}</h2>")
        html_parts.append("<ul>")
        for item in items:
            title = item.get("title", "")
            url = item.get("url", "")
            if url:
                html_parts.append(f'<li><a href="{url}">{title}</a></li>')
            else:
                html_parts.append(f"<li>{title}</li>")
        html_parts.append("</ul>")

    html_parts.append("</body></html>")
    return "\n".join(html_parts)


if __name__ == "__main__":
    # Test with sample data
    sample_news = [
        {
            "source": "Playwright",
            "title": "Playwright v1.40.0 Released",
            "url": "https://github.com/microsoft/playwright/releases/tag/v1.40.0",
            "summary": "New features including improved selectors and faster execution.",
        },
        {
            "source": "Hacker News",
            "title": "Show HN: A new testing framework",
            "url": "https://example.com/testing",
            "score": 150,
        },
        {
            "source": "TLDR",
            "title": "AI is changing software development",
            "url": "https://example.com/ai-dev",
            "summary": "How AI tools are reshaping the development workflow.",
        },
    ]

    print("Testing summarizer with sample data...\n")
    result = summarize(sample_news)
    print(result)
