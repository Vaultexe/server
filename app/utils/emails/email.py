from pathlib import Path
from typing import Any, Literal

from pydantic import EmailStr
from python_http_client.client import Response as EmailResponse
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Header, Mail

from app.core.config import settings
from app.schemas.email import (
    OTPEmailPayload,
    RegistrationEmailPayload,
)


def send_email(
    *,
    from_email: EmailStr = settings.EMAILS_FROM,
    to_emails: EmailStr | list[EmailStr],
    subject: str,
    body: str,
    environments: dict[str, Any] | None = None,
    ccs: EmailStr | list[EmailStr] | None = None,
    personized: bool = False,
) -> EmailResponse:
    """
    Send an email using SendGrid.
    """

    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=body,
        global_substitutions=environments,
        is_multiple=personized,
    )

    if ccs:
        if isinstance(ccs, list):
            for cc in ccs:
                message.add_cc(cc)
        else:
            message.add_cc(ccs)

    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

    return sg.send(message)  # type: ignore


def send_registration_email(data: RegistrationEmailPayload) -> EmailResponse:
    body = read_template("registration.html")
    return send_email(
        to_emails=data.to,
        subject=data.subject,
        body=body,
        ccs=data.ccs,
        environments={
            "__registration_link__": f"{settings.DOMAIN}/register?token={data.token}&email={data.to}",
            "__email__": str(data.to),
            "__expires_in__": str(data.expires_in_hours),
        },
    )


def send_otp_email(data: OTPEmailPayload) -> EmailResponse:
    body = read_template("otp.html")
    return send_email(
        to_emails=data.to,
        subject=data.subject,
        body=body,
        ccs=data.ccs,
        environments={
            "__otp__": str(data.otp),
            "__expires_at__": data.expires_at.strftime("%Y-%m-%d %H:%M:%S"),
        },
    )


def read_template(template_name: str) -> str:
    """Reads the email template"""
    with open(Path(__file__).parent / "templates" / template_name) as f:
        return f.read()


def set_priority(
    mail: Mail,
    priority: Literal["high", "normal", "low"] = "normal",
) -> None:
    """
    Set the priority of the email.

    Email clients support:
        x-priority: outlook, thunderbird
    """

    priority_level = {
        "high": "1",
        "normal": "3",
        "low": "5",
    }[priority]

    mail.add_header(Header("x-priority", priority_level))
