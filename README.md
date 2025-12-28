# Briefit

AQA팀을 위한 주간 IT 뉴스 브리핑 서비스. 여러 소스에서 뉴스를 수집하고 AI로 요약하여 이메일로 발송합니다.

## 수집 소스

| 소스 | 수집 기간 | 수집 개수 |
|------|----------|----------|
| Playwright Releases | 최근 7일 | 최대 5개 |
| Hacker News | 최근 7일 | Top 20 (점수순) |
| TLDR Newsletter | 최근 7일 (평일) | 일 3개씩 |
| OpenAI Blog | 최근 7일 | 최대 5개 |
| Anthropic News | 최근 7일 | 최대 5개 |
| Medium | 현재 인기글 | 최대 10개 |

## 프로젝트 구조

```
briefit/
├── collectors/          # 뉴스 수집기
├── summarizer/          # OpenAI 요약
├── sender/              # 이메일 발송
├── main.py              # 메인 실행
└── .github/workflows/   # GitHub Actions
```

## 환경변수

**필수**
- `OPENAI_API_KEY` - OpenAI API 키
- `RESEND_API_KEY` - Resend API 키
- `EMAIL_FROM` - 발신자 이메일
- `EMAIL_TO` - 수신자 이메일 (콤마 구분)

**선택**
- `MEDIUM_SESSION_ID` - Medium 세션 ID (유료 콘텐츠 접근용)

## 실행

```bash
# 로컬 실행
python main.py
```

GitHub Actions: 매주 월요일 오전 9시 (KST) 자동 실행
