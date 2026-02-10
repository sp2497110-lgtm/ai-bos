"""
Email Notification Service
Simulated email sending for development
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailService:
    """Email notification service (simulated for development)"""
    
    def __init__(self):
        self.enabled = True
        self.sent_emails = []
        
    def is_enabled(self) -> bool:
        """Check if email service is enabled"""
        return self.enabled
    
    def send_notice(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Send email notice (simulated in development)
        
        In production, this would integrate with:
        - AWS SES
        - SendGrid
        - SMTP server
        """
        try:
            if not self.is_enabled():
                return {
                    "success": False,
                    "error": "Email service is disabled",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Validate email (basic validation)
            if "@" not in to_email or "." not in to_email:
                return {
                    "success": False,
                    "error": "Invalid email address",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Simulate email sending
            email_record = {
                "to": to_email,
                "subject": subject,
                "body_preview": body[:100] + "..." if len(body) > 100 else body,
                "timestamp": datetime.now().isoformat(),
                "status": "sent",
                "message_id": f"EMAIL_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            # Store for logging (in production this would be actual email)
            self.sent_emails.append(email_record)
            
            logger.info(f"Email sent to {to_email}: {subject}")
            
            return {
                "success": True,
                "message_id": email_record["message_id"],
                "timestamp": email_record["timestamp"],
                "note": "Simulated email sent. In production, actual email would be delivered."
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_sent_emails(self, limit: int = 100) -> list:
        """Get history of sent emails"""
        return self.sent_emails[-limit:] if self.sent_emails else []
    
    def enable_service(self):
        """Enable email service"""
        self.enabled = True
        logger.info("Email service enabled")
    
    def disable_service(self):
        """Disable email service"""
        self.enabled = False
        logger.info("Email service disabled")