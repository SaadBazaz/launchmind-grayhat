import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_cold_outreach(subject: str, body: str) -> None:
    message = Mail(
        from_email=os.environ["SENDGRID_VERIFIED_SENDER_IDENTITY"],
        to_emails=os.environ["EMAIL_TO"],
        subject=subject,
        html_content=f"<p>{body.replace(chr(10), '<br>')}</p>",
    )
    sg = SendGridAPIClient(os.environ["SENDGRID_API_KEY"])
    response = sg.send(message)
    if response.status_code not in (200, 202):
        raise RuntimeError(f"SendGrid error: {response.status_code}")
