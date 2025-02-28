from .models import User, VerificationToken
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_verification_email(user_id, token):
    """Send email verification link to the user."""
    user = User.objects.get(id=user_id)
    verification_url = f"http://localhost:8000/api/auth/verify-email/?token={token}"
    subject = "Verify Your Email Address"
    message = f"""
    Dear {user.first_name},

    Please verify your email by clicking the link below:
    {verification_url}

    If you didn’t register, please ignore this email.

    Best regards,
    Job Board Team
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )