"""
Email service for PTT Site Watcher
Sends email notifications when changes are detected
Uses exchangelib for Exchange integration
"""
from exchangelib import Credentials, Account, Message, Mailbox, HTMLBody, Configuration, DELEGATE
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
from typing import List

# Disable SSL verification (for internal Exchange servers)
BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter


def format_change_html(change: dict) -> str:
    """Format a single change as HTML"""
    change_type = change.get("change_type", "unknown")
    title = change.get("title", "Unknown")
    detected_at = change.get("detected_at", "")
    link = change.get("new_content", "") or change.get("old_content", "")  # link is stored in content fields
    
    colors = {
        "new": "#22c55e",      # green
        "modified": "#f59e0b", # amber
        "removed": "#ef4444",  # red
    }
    color = colors.get(change_type, "#6b7280")
    
    labels = {
        "new": "🆕 YENİ",
        "modified": "✏️ DEĞİŞTİ",
        "removed": "🗑️ KALDIRILDI",
    }
    label = labels.get(change_type, "Bilinmiyor")
    
    # Create clickable title if link is available
    if link and change_type != "removed":
        title_html = f'<a href="{link}" style="color: #2563eb; text-decoration: none;">{title}</a>'
    else:
        title_html = title
    
    return f"""
    <tr>
        <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
            <span style="display: inline-block; padding: 4px 8px; border-radius: 4px; background-color: {color}; color: white; font-size: 12px; font-weight: bold;">
                {label}
            </span>
        </td>
        <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
            {title_html}
        </td>
        <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 12px;">
            {detected_at}
        </td>
    </tr>
    """


def create_email_html(changes: List[dict]) -> str:
    """Create HTML email body with change summary"""
    changes_html = "".join([format_change_html(c) for c in changes])
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f3f4f6; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 24px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">PTT Site Watcher</h1>
                <p style="color: rgba(255,255,255,0.8); margin: 8px 0 0 0; font-size: 14px;">
                    {len(changes)} change(s) detected
                </p>
            </div>
            
            <!-- Content -->
            <div style="padding: 24px;">
                <p style="color: #374151; margin: 0 0 16px 0;">
                    The following changes were detected on the PTT announcements page:
                </p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
                    <thead>
                        <tr style="background-color: #f9fafb;">
                            <th style="padding: 12px; text-align: left; font-size: 12px; text-transform: uppercase; color: #6b7280; border-bottom: 2px solid #e5e7eb;">Type</th>
                            <th style="padding: 12px; text-align: left; font-size: 12px; text-transform: uppercase; color: #6b7280; border-bottom: 2px solid #e5e7eb;">Title</th>
                            <th style="padding: 12px; text-align: left; font-size: 12px; text-transform: uppercase; color: #6b7280; border-bottom: 2px solid #e5e7eb;">Detected At</th>
                        </tr>
                    </thead>
                    <tbody>
                        {changes_html}
                    </tbody>
                </table>
                
                <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #e5e7eb;">
                    <a href="https://www.ptt.gov.tr/duyurular?page=1&announcementType=3" 
                       style="display: inline-block; padding: 12px 24px; background-color: #6366f1; color: white; text-decoration: none; border-radius: 6px; font-weight: 500;">
                        View PTT Announcements
                    </a>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f9fafb; padding: 16px 24px; text-align: center;">
                <p style="color: #9ca3af; margin: 0; font-size: 12px;">
                    This is an automated notification from PTT Site Watcher.
                </p>
            </div>
        </div>
    </body>
    </html>
    """


def send_change_notification(changes: List[dict], settings: dict) -> bool:
    """
    Send email notification for detected changes using Exchange
    
    Args:
        changes: List of change dictionaries
        settings: Settings dictionary with email configuration
        
    Returns:
        True if email was sent successfully
        
    Raises:
        Exception: If email sending fails with details
    """
    if not settings.get("email_enabled", False):
        raise Exception("Email notifications are disabled")
    
    recipients = settings.get("email_recipients", [])
    if not recipients:
        raise Exception("No email recipients configured")
    
    sender = settings.get("email_sender", "")
    if not sender:
        raise Exception("No sender email configured")
    
    smtp_username = settings.get("smtp_username", "")
    smtp_password = settings.get("smtp_password", "")
    exchange_server = settings.get("smtp_server", "mektup.dgpays.com")
    
    if not smtp_username or not smtp_password:
        raise Exception("Exchange credentials not configured")
    
    print(f"Connecting to Exchange server {exchange_server} as {smtp_username}...")
    
    # Create credentials (supports DOMAIN\\username format)
    credentials = Credentials(smtp_username, smtp_password)
    
    # Configure with explicit service endpoint (EWS URL)
    # Exchange servers typically expose EWS at /EWS/Exchange.asmx
    service_endpoint = f"https://{exchange_server}/EWS/Exchange.asmx"
    print(f"Using EWS endpoint: {service_endpoint}")
    
    config = Configuration(
        service_endpoint=service_endpoint,
        credentials=credentials
    )
    
    # Connect to Exchange account
    account = Account(
        primary_smtp_address=sender,
        config=config,
        autodiscover=False,
        access_type=DELEGATE
    )
    
    # Create message
    subject = f"PTT Site Watcher: {len(changes)} change(s) detected"
    html_content = create_email_html(changes)
    
    message = Message(
        account=account,
        subject=subject,
        body=HTMLBody(html_content),
        to_recipients=[Mailbox(email_address=r) for r in recipients]
    )
    
    # Send email
    print(f"Sending email to {recipients}...")
    message.send()
    
    print(f"Email sent successfully to {len(recipients)} recipient(s)")
    return True

