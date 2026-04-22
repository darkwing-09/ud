"""Email Celery tasks — verification, password reset, notifications."""
from __future__ import annotations

from app.workers.celery_app import celery_app


@celery_app.task(
    name="app.workers.tasks.email_tasks.send_email_verification",
    queue="default",
    max_retries=3,
    default_retry_delay=60,
    bind=True,
)
def send_email_verification(self, user_id: str, email: str, full_name: str, otp: str, token: str) -> dict:
    """Send email verification OTP to new user."""
    try:
        import resend
        from app.core.config import settings

        resend.api_key = settings.RESEND_API_KEY

        html_body = f"""
        <div style="font-family: Inter, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #6366f1;">Welcome to EduCore 🏫</h1>
            <p>Hi {full_name},</p>
            <p>Your verification OTP is:</p>
            <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #6366f1;">{otp}</span>
            </div>
            <p>This OTP expires in 24 hours.</p>
            <p>If you did not create an account, ignore this email.</p>
            <hr style="border: 1px solid #e5e7eb;">
            <p style="color: #6b7280; font-size: 12px;">EduCore School Management Platform</p>
        </div>
        """

        resend.Emails.send({
            "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
            "to": [email],
            "subject": "Verify your EduCore account — OTP inside",
            "html": html_body,
        })
        return {"status": "sent", "email": email}

    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task(
    name="app.workers.tasks.email_tasks.send_password_reset_email",
    queue="default",
    max_retries=3,
    default_retry_delay=60,
    bind=True,
)
def send_password_reset_email(self, email: str, full_name: str, otp: str, token: str) -> dict:
    """Send password reset OTP."""
    try:
        import resend
        from app.core.config import settings

        resend.api_key = settings.RESEND_API_KEY

        html_body = f"""
        <div style="font-family: Inter, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #6366f1;">Password Reset Request</h1>
            <p>Hi {full_name},</p>
            <p>Your password reset OTP is:</p>
            <div style="background: #fef3c7; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #d97706;">{otp}</span>
            </div>
            <p>This OTP expires in 2 hours. If you didn't request this, ignore this email.</p>
        </div>
        """

        resend.Emails.send({
            "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
            "to": [email],
            "subject": "EduCore Password Reset OTP",
            "html": html_body,
        })
        return {"status": "sent", "email": email}

    except Exception as exc:
        self.retry(exc=exc)
