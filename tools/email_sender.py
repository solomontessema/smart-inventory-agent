import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Optional
from langchain.tools import tool
from config import (
    AGENT_EMAIL_ADDRESS,
    AGENT_EMAIL_PASSWORD,
    RECIPIENT_EMAIL_ADDRESS
)

# If not in config, define fallbacks:
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_email(
    to_address: str,
    subject: str,
    body: str,
    attachment_path: Optional[str] = None
) -> str:
    """Send a plaintext email with optional attachment."""
    if not AGENT_EMAIL_ADDRESS or not AGENT_EMAIL_PASSWORD:
        raise ValueError("Missing email credentials (AGENT_EMAIL_ADDRESS or AGENT_EMAIL_PASSWORD).")

    msg = MIMEMultipart("alternative")    
    msg["From"] = AGENT_EMAIL_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    msg.attach(MIMEText(body, "html")) 

    if attachment_path:
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=attachment_path)
        part["Content-Disposition"] = f'attachment; filename="{attachment_path}"'
        msg.attach(part)
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(AGENT_EMAIL_ADDRESS, AGENT_EMAIL_PASSWORD)
        server.send_message(msg)

    return "Email sent successfully."

@tool
def send_email_tool(input_str: str) -> str:
    """Send an email to the recipient. Input format: 'subject || body'."""
    subject, body = [x.strip() for x in input_str.split("||", 1)]

    try:
        result = send_email(
            to_address=RECIPIENT_EMAIL_ADDRESS,
            subject=subject,
            body=body
        )
        return result
    except Exception as e:
        return f"Failed to send email: {e}"