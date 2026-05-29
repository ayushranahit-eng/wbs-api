import base64
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from core.config import settings


def _get_gmail_service():
    creds = Credentials(
        token=None,
        refresh_token=settings.GMAIL_REFRESH_TOKEN,
        client_id=settings.GMAIL_CLIENT_ID,
        client_secret=settings.GMAIL_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
    )
    creds.refresh(Request())
    return build("gmail", "v1", credentials=creds)


def send_wbs_email(recipient: str, project_title: str, full_wbs_path: str, sales_wbs_path: str):
    service = _get_gmail_service()

    msg = MIMEMultipart()
    msg["From"] = settings.GMAIL_SENDER
    msg["To"] = recipient
    msg["Subject"] = f"WBS Generated – {project_title}"

    html_body = f"""
    <html>
    <body style="margin:0;padding:0;background-color:#f4f6f9;font-family:'Segoe UI',Arial,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f6f9;padding:40px 0;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">

                        <!-- Header -->
                        <tr>
                            <td style="background-color:#1a73e8;padding:36px 40px;text-align:center;">
                                <h1 style="margin:0;color:#ffffff;font-size:24px;font-weight:700;letter-spacing:0.5px;">Work Breakdown Structure</h1>
                                <p style="margin:8px 0 0;color:#d2e3fc;font-size:14px;">AI Generated — Ready for Review</p>
                            </td>
                        </tr>

                        <!-- Body -->
                        <tr>
                            <td style="padding:36px 40px;">
                                <p style="margin:0 0 16px;font-size:15px;color:#3c4043;">Hi,</p>
                                <p style="margin:0 0 24px;font-size:15px;color:#3c4043;line-height:1.6;">
                                    Your Work Breakdown Structure for <strong>{project_title}</strong> has been successfully generated and is attached to this email.
                                </p>

                                <!-- Info Box -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f8f9fa;border-left:4px solid #1a73e8;border-radius:4px;margin-bottom:28px;">
                                    <tr>
                                        <td style="padding:16px 20px;">
                                            <p style="margin:0;font-size:13px;color:#5f6368;text-transform:uppercase;letter-spacing:0.8px;font-weight:600;">Project Details</p>
                                            <p style="margin:8px 0 0;font-size:15px;color:#202124;"><strong>Project:</strong> {project_title}</p>
                                        </td>
                                    </tr>
                                </table>

                                <!-- Attachments -->
                                <p style="margin:0 0 12px;font-size:14px;font-weight:600;color:#202124;">Attached Files</p>
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
                                    <tr>
                                        <td style="padding:10px 16px;background-color:#e8f0fe;border-radius:6px;margin-bottom:8px;display:block;">
                                            <span style="font-size:18px;">📊</span>
                                            <span style="font-size:14px;color:#1a73e8;font-weight:600;margin-left:8px;">Full WBS</span>
                                            <span style="font-size:13px;color:#5f6368;margin-left:6px;">— Complete breakdown for internal use</span>
                                        </td>
                                    </tr>
                                    <tr><td style="height:8px;"></td></tr>
                                    <tr>
                                        <td style="padding:10px 16px;background-color:#e6f4ea;border-radius:6px;display:block;">
                                            <span style="font-size:18px;">📋</span>

                                            <span style="font-size:14px;color:#188038;font-weight:600;margin-left:8px;">Sales WBS</span>
                                            <span style="font-size:13px;color:#5f6368;margin-left:6px;">— Simplified copy for client presentation</span>
                                        </td>
                                    </tr>
                                </table>

                                <p style="margin:0;font-size:14px;color:#5f6368;line-height:1.6;">
                                    Please review the attached files and reach out if any changes are needed.
                                </p>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="background-color:#f8f9fa;padding:24px 40px;border-top:1px solid #e8eaed;text-align:center;">
                                <p style="margin:0;font-size:13px;color:#9aa0a6;">This email was generated automatically by the WBS AI System.</p>
                                <p style="margin:6px 0 0;font-size:13px;color:#9aa0a6;">Please do not reply to this email.</p>
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    msg.attach(MIMEText(html_body, "html"))

    for path in [full_wbs_path, sales_wbs_path]:
        abs_path = os.path.abspath(path)
        with open(abs_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(abs_path)}")
        msg.attach(part)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
