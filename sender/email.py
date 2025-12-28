"""
Email Sender using Resend
- 요약된 뉴스레터를 팀에게 이메일로 발송
"""

import os
from datetime import datetime
import resend


def send(content: str, subject: str = None) -> bool:
    """
    Send email newsletter to team using Resend.

    Args:
        content: HTML content to send
        subject: Email subject (optional, auto-generated if not provided)

    Returns:
        True if email sent successfully, False otherwise
    """
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        print("[Email] RESEND_API_KEY not set")
        return False

    email_from = os.getenv("EMAIL_FROM", "briefit@yourdomain.com")
    email_to = os.getenv("EMAIL_TO", "")

    if not email_to:
        print("[Email] EMAIL_TO not set")
        return False

    # Parse recipients (comma-separated)
    recipients = [e.strip() for e in email_to.split(",") if e.strip()]
    if not recipients:
        print("[Email] No valid recipients found")
        return False

    # Generate subject if not provided
    if not subject:
        today = datetime.now()
        week_num = today.isocalendar()[1]
        subject = f"📡 Weekly IT Briefing - {today.year}년 {week_num}주차"

    resend.api_key = api_key

    try:
        response = resend.Emails.send({
            "from": email_from,
            "to": recipients,
            "subject": subject,
            "html": content,
        })

        email_id = response.get("id") if isinstance(response, dict) else getattr(response, "id", None)
        print(f"[Email] Successfully sent to {len(recipients)} recipient(s)")
        print(f"[Email] Email ID: {email_id}")
        return True

    except Exception as e:
        print(f"[Email] Error sending email: {e}")
        return False


def send_test(to_email: str = None) -> bool:
    """
    Send a test email to verify configuration.

    Args:
        to_email: Test recipient email (optional, uses EMAIL_TO if not provided)

    Returns:
        True if test email sent successfully
    """
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        print("[Email] RESEND_API_KEY not set")
        return False

    email_from = os.getenv("EMAIL_FROM", "briefit@yourdomain.com")
    recipient = to_email or os.getenv("EMAIL_TO", "").split(",")[0]

    if not recipient:
        print("[Email] No recipient specified")
        return False

    resend.api_key = api_key

    test_content = """
    <html>
    <body>
        <h1>📡 Briefit Test Email</h1>
        <p>이 이메일은 Briefit 설정 테스트입니다.</p>
        <p>이 메일을 받으셨다면 이메일 설정이 올바르게 구성되었습니다.</p>
        <hr>
        <p><em>Briefit - AI-powered IT news briefing service</em></p>
    </body>
    </html>
    """

    try:
        response = resend.Emails.send({
            "from": email_from,
            "to": [recipient],
            "subject": "🧪 Briefit Test Email",
            "html": test_content,
        })

        email_id = response.get("id") if isinstance(response, dict) else getattr(response, "id", None)
        print(f"[Email] Test email sent to {recipient}")
        print(f"[Email] Email ID: {email_id}")
        return True

    except Exception as e:
        print(f"[Email] Test email failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing email sender...\n")

    # Check environment
    api_key = os.getenv("RESEND_API_KEY")
    email_to = os.getenv("EMAIL_TO")

    print(f"RESEND_API_KEY: {'Set' if api_key else 'Not set'}")
    print(f"EMAIL_TO: {email_to or 'Not set'}")

    if api_key and email_to:
        print("\nSending test email...")
        success = send_test()
        print(f"\nResult: {'Success' if success else 'Failed'}")
    else:
        print("\nConfigure environment variables to test email sending.")
