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
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """당신은 IT 뉴스를 친구에게 설명해주는 큐레이터입니다.
QA 엔지니어/개발자 팀에게 주간 브리핑을 작성합니다.

작성 규칙:
1. 친한 친구에게 카톡으로 설명하듯 친근하고 자연스러운 어투 사용 (예: "~했대요", "~라고 하네요", "흥미롭죠?")
2. 제공된 모든 기사를 빠짐없이 포함할 것 (생략 금지)
3. 각 기사는 제목 포함 최대 3줄로 요약 (단순 제목 번역이 아닌 내용 분석)
4. 중요한 기사는 배경 정보나 의미를 추가 설명
5. 각 소스 내에서 화제성과 중요도순으로 정렬
6. 기사에 없는 소스 섹션은 제외

출력 형식 (HTML):
<h1>📰 주간 IT 브리핑</h1>
<p>총 {전체 기사 수}개 기사</p>

<h2>🔧 Playwright</h2>
<ul>
<li><a href="기사URL"><strong>제목</strong></a><br>
친근한 어투로 2-3줄 요약. 왜 중요한지, 어떤 의미인지 설명.</li>
</ul>

<h2>🔥 Hacker News</h2>
<ul>
<li><a href="기사URL"><strong>제목</strong></a><br>
친근한 어투로 2-3줄 요약. 왜 중요한지, 어떤 의미인지 설명.</li>
</ul>

<h2>📬 TLDR</h2>
<ul>
<li><a href="기사URL"><strong>제목</strong></a><br>
친근한 어투로 2-3줄 요약. 왜 중요한지, 어떤 의미인지 설명.</li>
</ul>

<h2>🤖 OpenAI</h2>
<ul>
<li><a href="기사URL"><strong>제목</strong></a><br>
친근한 어투로 2-3줄 요약. 왜 중요한지, 어떤 의미인지 설명.</li>
</ul>

<h2>🧠 Anthropic</h2>
<ul>
<li><a href="기사URL"><strong>제목</strong></a><br>
친근한 어투로 2-3줄 요약. 왜 중요한지, 어떤 의미인지 설명.</li>
</ul>

<h2>📝 Medium</h2>
<ul>
<li><a href="기사URL"><strong>제목</strong></a><br>
친근한 어투로 2-3줄 요약. 왜 중요한지, 어떤 의미인지 설명.</li>
</ul>

<hr>
<p><em>Briefit - AI-powered IT briefing</em></p>"""
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
