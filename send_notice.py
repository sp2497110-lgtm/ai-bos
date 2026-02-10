"""
Notice Sending Module
Handles notification workflows
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

from backend.integrations.notification.email import EmailService
from backend.integrations.notification.sms import SMSService

logger = logging.getLogger(__name__)

class NoticeSender:
    """Orchestrates sending of notices based on penalty decisions"""
    
    def __init__(self):
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.notification_log = []
        
    def send_penalty_notice(self, 
                           calculation_result: Dict[str, Any],
                           recipient_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send penalty notice via email and/or SMS
        """
        try:
            delay_minutes = calculation_result.get("delay_minutes", 0)
            penalty_amount = calculation_result.get("penalty_amount", 0)
            rule_applied = calculation_result.get("rule_applied", "")
            
            # Prepare notice content
            notice_content = self._prepare_notice_content(
                delay_minutes=delay_minutes,
                penalty_amount=penalty_amount,
                rule_applied=rule_applied,
                recipient_info=recipient_info
            )
            
            # Track notifications sent
            notifications_sent = {
                "email": False,
                "sms": False,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send email notification
            if recipient_info.get("email") and self.email_service.is_enabled():
                email_result = self.email_service.send_notice(
                    to_email=recipient_info["email"],
                    subject=notice_content["email_subject"],
                    body=notice_content["email_body"]
                )
                notifications_sent["email"] = email_result["success"]
                
                if email_result["success"]:
                    logger.info(f"Email notice sent to {recipient_info['email']}")
            
            # Send SMS notification
            if recipient_info.get("phone") and self.sms_service.is_enabled():
                sms_result = self.sms_service.send_notice(
                    to_phone=recipient_info["phone"],
                    message=notice_content["sms_message"]
                )
                notifications_sent["sms"] = sms_result["success"]
                
                if sms_result["success"]:
                    logger.info(f"SMS notice sent to {recipient_info['phone']}")
            
            # Log the notification
            self._log_notification(
                calculation_result=calculation_result,
                recipient_info=recipient_info,
                notifications_sent=notifications_sent
            )
            
            return {
                "notice_id": f"NOTICE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "status": "sent",
                "notifications": notifications_sent,
                "content_preview": {
                    "subject": notice_content["email_subject"],
                    "sms_preview": notice_content["sms_message"][:50] + "..."
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to send notice: {e}")
            return {
                "notice_id": None,
                "status": "failed",
                "error": str(e),
                "notifications": {"email": False, "sms": False}
            }
    
    def _prepare_notice_content(self, 
                               delay_minutes: int,
                               penalty_amount: float,
                               rule_applied: str,
                               recipient_info: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare notice content based on penalty details"""
        
        # Email subject
        if penalty_amount > 0:
            subject = f"Penalty Notice: ₹{penalty_amount:,.2f} for {delay_minutes}min Delay"
        else:
            subject = f"Delay Notification: {delay_minutes}min Delay - No Penalty"
        
        # Email body
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2>AI-BOS Notification</h2>
            <p><strong>Recipient:</strong> {recipient_info.get('name', 'Valued Partner')}</p>
            <p><strong>Date:</strong> {datetime.now().strftime('%d %B, %Y %H:%M IST')}</p>
            <hr>
            
            <h3>Delay Analysis Report</h3>
            <table style="border-collapse: collapse; width: 100%;">
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;"><strong>Delay Duration</strong></td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{delay_minutes} minutes</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;"><strong>Rule Applied</strong></td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{rule_applied}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;"><strong>Penalty Amount</strong></td>
                    <td style="border: 1px solid #ddd; padding: 8px;">₹{penalty_amount:,.2f}</td>
                </tr>
            </table>
            
            <p><strong>Business Impact:</strong> This delay has been recorded in our SLA monitoring system.</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; margin-top: 20px; border-left: 4px solid #007bff;">
                <p><strong>Next Steps:</strong></p>
                <ul>
                    <li>Review the delay details in your dashboard</li>
                    <li>Contact operations team for clarification</li>
                    <li>Implement corrective measures if needed</li>
                </ul>
            </div>
            
            <p style="margin-top: 30px; color: #666; font-size: 12px;">
                This is an automated notification from AI-BOS (AI-Based Operations System).
                Please do not reply to this email.
            </p>
        </body>
        </html>
        """
        
        # SMS message (concise)
        if penalty_amount > 0:
            sms_message = f"AI-BOS: {delay_minutes}min delay. Penalty: ₹{penalty_amount:,.2f}. Check email for details."
        else:
            sms_message = f"AI-BOS: {delay_minutes}min delay recorded. No penalty applied. Details in email."
        
        return {
            "email_subject": subject,
            "email_body": email_body.strip(),
            "sms_message": sms_message
        }
    
    def _log_notification(self,
                         calculation_result: Dict[str, Any],
                         recipient_info: Dict[str, Any],
                         notifications_sent: Dict[str, Any]):
        """Log notification for audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "delay_minutes": calculation_result.get("delay_minutes"),
            "penalty_amount": calculation_result.get("penalty_amount"),
            "recipient": {
                "name": recipient_info.get("name"),
                "email": recipient_info.get("email"),
                "phone": recipient_info.get("phone")
            },
            "notifications": notifications_sent,
            "rule_applied": calculation_result.get("rule_applied")
        }
        
        self.notification_log.append(log_entry)
        
        # Keep only last 1000 logs
        if len(self.notification_log) > 1000:
            self.notification_log = self.notification_log[-1000:]
    
    def get_notification_logs(self, limit: int = 50) -> list:
        """Get recent notification logs"""
        return self.notification_log[-limit:] if self.notification_log else []