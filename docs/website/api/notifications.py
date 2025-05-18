"""
Email notification system for the PlainSpeak Plugin Development Contest.
"""

import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from jinja2 import Environment, FileSystemLoader

# Email configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "contest@plainspeak.org")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Load email templates
template_env = Environment(loader=FileSystemLoader("templates/emails"))


class EmailNotifier:
    """Handles email notifications for contest events."""

    async def send_email(self, to_email: str, subject: str, template_name: str, context: dict) -> None:
        """
        Send an email using a template.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            template_name: Name of the template file
            context: Template context variables
        """
        template = template_env.get_template(f"{template_name}.html")
        html_content = template.render(**context)

        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"PlainSpeak Contest <{SMTP_USER}>"
        message["To"] = to_email

        # Add HTML content
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        # Send email
        try:
            await aiosmtplib.send(
                message,
                hostname=SMTP_HOST,
                port=SMTP_PORT,
                username=SMTP_USER,
                password=SMTP_PASSWORD,
                use_tls=True,
            )
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            raise


async def send_registration_confirmation(email: str, name: str, participant_id: str) -> None:
    """Send registration confirmation email."""
    notifier = EmailNotifier()
    await notifier.send_email(
        to_email=email,
        subject="Welcome to the PlainSpeak Plugin Contest!",
        template_name="registration_confirmation",
        context={
            "name": name,
            "participant_id": participant_id,
            "dashboard_url": f"https://contest.plainspeak.org/dashboard/{participant_id}",
        },
    )


async def send_submission_confirmation(email: str, name: str) -> None:
    """Send submission confirmation email."""
    notifier = EmailNotifier()
    await notifier.send_email(
        to_email=email,
        subject="Plugin Submission Received",
        template_name="submission_confirmation",
        context={"name": name},
    )


async def send_judging_complete(email: str, name: str, score: float, feedback: str) -> None:
    """Send judging results email."""
    notifier = EmailNotifier()
    await notifier.send_email(
        to_email=email,
        subject="Your Plugin Has Been Judged",
        template_name="judging_complete",
        context={"name": name, "score": score, "feedback": feedback},
    )


async def send_winner_notification(email: str, name: str, category: str, prize: str) -> None:
    """Send winner notification email."""
    notifier = EmailNotifier()
    await notifier.send_email(
        to_email=email,
        subject="Congratulations - You're a Winner!",
        template_name="winner_notification",
        context={"name": name, "category": category, "prize": prize},
    )


async def send_deadline_reminder(email: str, name: str, days_left: int) -> None:
    """Send submission deadline reminder."""
    notifier = EmailNotifier()
    await notifier.send_email(
        to_email=email,
        subject=f"Reminder: {days_left} Days Until Submission Deadline",
        template_name="deadline_reminder",
        context={"name": name, "days_left": days_left},
    )
