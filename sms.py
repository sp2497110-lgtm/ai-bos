"""
SMS Notification Service
Simulated SMS sending for development
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class SMSService:
    """SMS notification service (simulated for development)"""
    
    def __init__(self):
        self.enabled = True
        self.sent_sms = []
        
    def is_enabled(self) -> bool:
        """Check if SMS service is enabled"""
        return self.enabled
    
    def send_notice(self, to_phone: str, message: str) -> Dict[str, Any]:
        """
        Send SMS notice (simulated in development)
        
        In production, this would integrate with:
        - Twilio
        - AWS SNS
        - TextLocal
        - Fast2SMS
        """
        try:
            if not self.is_enabled():
                return {
                    "success": False,
                    "error": "SMS service is disabled",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Validate phone number (basic validation)
            if not to_phone or len(to_phone) < 10:
                return {
                    "success": False,
                    "error": "Invalid phone number",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Truncate message if too long
            if len(message) > 160:
                message = message[:157] + "..."
            
            # Simulate SMS sending
            sms_record = {
                "to": to_phone,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "status": "sent",
                "message_id": f"SMS_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "characters": len(message)
            }
            
            # Store for logging (in production this would be actual SMS)
            self.sent_sms.append(sms_record)
            
            logger.info(f"SMS sent to {to_phone}: {message[:30]}...")
            
            return {
                "success": True,
                "message_id": sms_record["message_id"],
                "timestamp": sms_record["timestamp"],
                "note": "Simulated SMS sent. In production, actual SMS would be delivered."
            }
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_phone}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_sent_sms(self, limit: int = 100) -> list:
        """Get history of sent SMS"""
        return self.sent_sms[-limit:] if self.sent_sms else []
    
    def enable_service(self):
        """Enable SMS service"""
        self.enabled = True
        logger.info("SMS service enabled")
    
    def disable_service(self):
        """Disable SMS service"""
        self.enabled = False
        logger.info("SMS service disabled")