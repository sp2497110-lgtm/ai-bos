"""
AI-BOS Configuration Settings
Enterprise-grade configuration management
"""

import os
from typing import Dict, Any

class Settings:
    """Centralized configuration management"""
    
    # Application Settings
    APP_NAME = "AI-BOS"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # AI Engine Configuration
    AI_PROVIDER = "anthropic"  # Simulated - in production would use actual AI service
    AI_MODEL = "claude-3-haiku"
    MAX_AI_TOKENS = 1000
    
    # Business Rules Configuration
    PENALTY_THRESHOLDS = {
        "no_penalty_max": 30,  # minutes
        "low_penalty_min": 31,
        "low_penalty_max": 60,
        "high_penalty_min": 61
    }
    
    PENALTY_AMOUNTS = {
        "fixed_penalty": 500.00,  # INR
        "variable_rate": 25.00,   # INR per minute over threshold
        "high_penalty_base": 1000.00
    }
    
    # Notification Settings
    EMAIL_ENABLED = True
    SMS_ENABLED = True
    NOTIFICATION_TEMPLATES = {
        "penalty_applied": "Penalty Notification",
        "warning": "Delay Warning",
        "no_penalty": "Compliance Confirmation"
    }
    
    # Security Settings
    API_KEY_HEADER = "X-API-Key"
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_PERIOD = 60  # seconds
    
    # Frontend Settings
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8000")
    CORS_ORIGINS = [
        "http://localhost:8000",
        "http://localhost:3000",
        "https://app.ai-bos.com"
    ]
    
    @classmethod
    def get_penalty_config(cls) -> Dict[str, Any]:
        """Get penalty configuration for business rules"""
        return {
            "thresholds": cls.PENALTY_THRESHOLDS,
            "amounts": cls.PENALTY_AMOUNTS
        }


settings = Settings()