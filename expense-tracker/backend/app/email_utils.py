import os
import logging
import resend
from disposable_email_domains import blocklist

logger = logging.getLogger(__name__)

def is_disposable_email(email: str) -> bool:
    """Check if the email domain is in the disposable email blocklist."""
    try:
        domain = email.split('@')[1].lower()
        return domain in blocklist
    except IndexError:
        return False

def send_otp_email(to_email: str, otp_code: str):
    """
    Send OTP email using Resend API. 
    If RESEND_API_KEY is missing, print the email to console for development purposes.
    """
    resend_api_key = os.environ.get("RESEND_API_KEY", "").strip()
    
    if not resend_api_key or resend_api_key == "re_your_api_key_here":
        logger.warning("RESEND_API_KEY is not configured. Falling back to console print.")
        print(f"========== OTP EMAIL (MOCK) ==========")
        print(f"To: {to_email}")
        print(f"Subject: Your Expense Tracker OTP")
        print(f"Body: Your verification code is: {otp_code}")
        print(f"======================================")
        return
        
    resend.api_key = resend_api_key
    
    html_content = f"""
    <div style="font-family: sans-serif; max-width: 500px; margin: 0 auto; padding: 20px; border: 1px solid #eaeaea; border-radius: 10px;">
        <h2 style="color: #333;">Expense Tracker Verification</h2>
        <p style="color: #555;">Your verification code is:</p>
        <div style="background-color: #f4f4f5; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0;">
            <strong style="font-size: 24px; letter-spacing: 5px; color: #111;">{otp_code}</strong>
        </div>
        <p style="color: #777; font-size: 12px;">This code will expire in 15 minutes.</p>
    </div>
    """

    try:
        r = resend.Emails.send({
            "from": "Expense Tracker <onboarding@resend.dev>",
            "to": to_email,
            "subject": "Your Expense Tracker OTP",
            "html": html_content
        })
        logger.info(f"Resend email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email via Resend: {e}")
        # Fallback to console print so the user is not blocked during development
        print(f"========== OTP EMAIL (FALLBACK MOCK) ==========")
        print(f"To: {to_email}")
        print(f"Subject: Your Expense Tracker OTP")
        print(f"Body: Your verification code is: {otp_code}")
        print(f"===============================================")
