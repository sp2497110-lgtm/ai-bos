"""
Business Rules Engine for Penalty Calculations
Deterministic rule-based calculations
"""

from typing import Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP
import logging

from config.settings import settings

logger = logging.getLogger(__name__)

class PenaltyCalculator:
    """Core penalty calculation engine with deterministic rules"""
    
    def __init__(self):
        self.config = settings.get_penalty_config()
        self.thresholds = self.config["thresholds"]
        self.amounts = self.config["amounts"]
        
    def calculate(self, delay_minutes: int, service_type: str = "standard") -> Dict[str, Any]:
        """
        Calculate penalty based on delay minutes and service type
        
        Rules:
        1. 0-30 minutes: No penalty
        2. 31-60 minutes: Fixed penalty
        3. 61+ minutes: Base penalty + per-minute overage
        """
        try:
            # Validate input
            if not isinstance(delay_minutes, (int, float)) or delay_minutes < 0:
                raise ValueError(f"Invalid delay minutes: {delay_minutes}")
            
            delay_minutes = int(delay_minutes)
            
            # Apply business rules
            if delay_minutes <= self.thresholds["no_penalty_max"]:
                return self._apply_no_penalty_rule(delay_minutes, service_type)
            
            elif delay_minutes <= self.thresholds["low_penalty_max"]:
                return self._apply_low_penalty_rule(delay_minutes, service_type)
            
            else:
                return self._apply_high_penalty_rule(delay_minutes, service_type)
                
        except Exception as e:
            logger.error(f"Penalty calculation failed: {e}")
            raise
    
    def _apply_no_penalty_rule(self, delay_minutes: int, service_type: str) -> Dict[str, Any]:
        """Apply rule for delays within acceptable threshold"""
        penalty_amount = Decimal('0.00')
        
        result = {
            "delay_minutes": delay_minutes,
            "penalty_applied": False,
            "penalty_amount": float(penalty_amount),
            "rule_applied": "no_penalty_threshold",
            "rule_description": f"Delay ≤ {self.thresholds['no_penalty_max']} minutes",
            "calculation_breakdown": {
                "base_amount": 0.00,
                "variable_amount": 0.00,
                "total": 0.00
            },
            "service_type": service_type,
            "threshold_exceeded": False
        }
        
        logger.info(f"No penalty applied for {delay_minutes}min delay")
        return result
    
    def _apply_low_penalty_rule(self, delay_minutes: int, service_type: str) -> Dict[str, Any]:
        """Apply fixed penalty for moderate delays"""
        penalty_amount = Decimal(str(self.amounts["fixed_penalty"]))
        
        result = {
            "delay_minutes": delay_minutes,
            "penalty_applied": True,
            "penalty_amount": float(penalty_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            "rule_applied": "fixed_penalty_rule",
            "rule_description": f"Delay {self.thresholds['low_penalty_min']}-{self.thresholds['low_penalty_max']} minutes",
            "calculation_breakdown": {
                "base_amount": float(penalty_amount),
                "variable_amount": 0.00,
                "total": float(penalty_amount)
            },
            "service_type": service_type,
            "threshold_exceeded": True,
            "exceeded_by_minutes": delay_minutes - self.thresholds["no_penalty_max"]
        }
        
        logger.info(f"Fixed penalty applied: ₹{penalty_amount} for {delay_minutes}min delay")
        return result
    
    def _apply_high_penalty_rule(self, delay_minutes: int, service_type: str) -> Dict[str, Any]:
        """Apply progressive penalty for significant delays"""
        # Calculate overage minutes
        overage_minutes = delay_minutes - self.thresholds["low_penalty_max"]
        
        # Calculate base penalty
        base_amount = Decimal(str(self.amounts["high_penalty_base"]))
        
        # Calculate variable penalty
        variable_rate = Decimal(str(self.amounts["variable_rate"]))
        variable_amount = variable_rate * Decimal(str(overage_minutes))
        
        # Calculate total
        total_amount = base_amount + variable_amount
        
        result = {
            "delay_minutes": delay_minutes,
            "penalty_applied": True,
            "penalty_amount": float(total_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            "rule_applied": "progressive_penalty_rule",
            "rule_description": f"Delay > {self.thresholds['low_penalty_max']} minutes",
            "calculation_breakdown": {
                "base_amount": float(base_amount),
                "variable_amount": float(variable_amount.quantize(Decimal('0.01'))),
                "per_minute_rate": float(variable_rate),
                "overage_minutes": overage_minutes,
                "total": float(total_amount.quantize(Decimal('0.01')))
            },
            "service_type": service_type,
            "threshold_exceeded": True,
            "exceeded_by_minutes": delay_minutes - self.thresholds["no_penalty_max"],
            "critical_delay": delay_minutes > 120  # Additional business logic
        }
        
        logger.info(f"Progressive penalty applied: ₹{total_amount} for {delay_minutes}min delay")
        return result
    
    def validate_rules(self) -> Dict[str, Any]:
        """Validate all business rules for consistency"""
        validation_results = {
            "rules_valid": True,
            "issues": [],
            "threshold_checks": {},
            "amount_checks": {}
        }
        
        # Check threshold consistency
        thresholds = [
            ("no_penalty_max", self.thresholds["no_penalty_max"]),
            ("low_penalty_min", self.thresholds["low_penalty_min"]),
            ("low_penalty_max", self.thresholds["low_penalty_max"]),
            ("high_penalty_min", self.thresholds["high_penalty_min"])
        ]
        
        for name, value in thresholds:
            if value < 0:
                validation_results["issues"].append(f"Negative threshold: {name}")
                validation_results["rules_valid"] = False
            validation_results["threshold_checks"][name] = {
                "value": value,
                "valid": value >= 0
            }
        
        # Check amount consistency
        if self.amounts["fixed_penalty"] <= 0:
            validation_results["issues"].append("Fixed penalty must be positive")
            validation_results["rules_valid"] = False
            
        if self.amounts["variable_rate"] <= 0:
            validation_results["issues"].append("Variable rate must be positive")
            validation_results["rules_valid"] = False
        
        validation_results["amount_checks"] = {
            "fixed_penalty": self.amounts["fixed_penalty"],
            "variable_rate": self.amounts["variable_rate"],
            "high_penalty_base": self.amounts["high_penalty_base"]
        }
        
        return validation_results