"""
Decision Engine for AI-powered business decisions
"""

from typing import Dict, Any
from datetime import datetime
import logging

from backend.ai_engine.ai_client import AIClient

logger = logging.getLogger(__name__)

class DecisionEngine:
    """Orchestrates AI explanations for business decisions"""
    
    def __init__(self):
        self.ai_client = AIClient()
        self.decision_logs = []
        
    def explain_penalty(self, delay_minutes: int, penalty_amount: float, rule_applied: str) -> Dict[str, Any]:
        """
        Generate AI explanation for applied penalty
        """
        context = {
            "delay_minutes": delay_minutes,
            "penalty_amount": penalty_amount,
            "rule_applied": rule_applied,
            "decision_type": "penalty_applied",
            "timestamp": datetime.now().isoformat()
        }
        
        explanation = self.ai_client.generate_explanation(context)
        
        # Log the decision
        self._log_decision(
            decision_type="penalty_explanation",
            context=context,
            ai_response=explanation
        )
        
        return explanation
    
    def explain_no_penalty(self, delay_minutes: int) -> Dict[str, Any]:
        """
        Generate AI explanation for no penalty case
        """
        context = {
            "delay_minutes": delay_minutes,
            "penalty_amount": 0.0,
            "rule_applied": "no_penalty_threshold",
            "decision_type": "no_penalty",
            "timestamp": datetime.now().isoformat()
        }
        
        explanation = self.ai_client.generate_explanation(context)
        
        # Log the decision
        self._log_decision(
            decision_type="no_penalty_explanation",
            context=context,
            ai_response=explanation
        )
        
        return explanation
    
    def analyze_trend(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze delay trends using simulated AI
        """
        try:
            delays = historical_data.get("delays", [])
            if not delays:
                return {
                    "analysis": "Insufficient data for trend analysis",
                    "confidence": 0.0
                }
            
            avg_delay = sum(delays) / len(delays)
            max_delay = max(delays)
            
            analysis = f"""
            Trend Analysis Results:
            - Average delay: {avg_delay:.1f} minutes
            - Maximum delay: {max_delay} minutes
            - Total observations: {len(delays)}
            
            Recommendations:
            {"Consider reviewing operational processes" if avg_delay > 20 else "Current performance is within acceptable range"}
            """
            
            return {
                "analysis": analysis.strip(),
                "metrics": {
                    "average_delay": avg_delay,
                    "max_delay": max_delay,
                    "data_points": len(delays)
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return {
                "analysis": "Unable to perform trend analysis",
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    def _log_decision(self, decision_type: str, context: Dict[str, Any], ai_response: Dict[str, Any]):
        """Log decision for audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "decision_type": decision_type,
            "context": context,
            "ai_response": ai_response,
            "system_version": "1.0.0"
        }
        
        self.decision_logs.append(log_entry)
        
        # Keep only last 1000 logs in memory
        if len(self.decision_logs) > 1000:
            self.decision_logs = self.decision_logs[-1000:]
        
        logger.info(f"Decision logged: {decision_type} - Delay: {context.get('delay_minutes')}min")
    
    def get_decision_logs(self, limit: int = 100) -> list:
        """Get recent decision logs"""
        return self.decision_logs[-limit:] if self.decision_logs else []