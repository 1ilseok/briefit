import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Email
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM", "briefit@yourdomain.com")
EMAIL_TO = os.getenv("EMAIL_TO", "").split(",")

# Medium
MEDIUM_SESSION_ID = os.getenv("MEDIUM_SESSION_ID")

# Data sources
SOURCES = {
    "playwright": {
        "url": "https://api.github.com/repos/microsoft/playwright/releases",
        "enabled": True,
    },
    "hackernews": {
        "url": "https://hacker-news.firebaseio.com/v0",
        "enabled": True,
    },
    "tldr": {
        "url": "https://tldr.tech",
        "enabled": True,
    },
    "openai_blog": {
        "url": "https://openai.com/blog",
        "enabled": True,
    },
    "anthropic_news": {
        "url": "https://www.anthropic.com/news",
        "enabled": True,
    },
    "medium": {
        "url": "https://medium.com",
        "enabled": True,
    },
}
