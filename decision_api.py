"""
Decision API Endpoints
Handles all business decision calculations and AI explanations
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

from backend.ai_engine.decision_engine import DecisionEngine
from backend.rules.penalty_rules import PenaltyCalculator
from config.settings import settings

router = APIRouter()

# Initialize engines
decision_engine = DecisionEngine()
penalty_calculator = PenaltyCalculator()

class CalculationRequest(BaseModel):
    """Request model for penalty calculation"""
    delay_minutes: int = Field(..., ge=0, le=1440, description="Delay in minutes (0-1440)")
    contract_id: Optional[str] = Field(None, description="Optional contract identifier")
    service_type: Optional[str] = Field("standard", description="Type of service")
    
    @validator('delay_minutes')
    def validate_delay_minutes(cls, v):
        if v > 1440:  # Max 24 hours
            raise ValueError("Delay cannot exceed 24 hours (1440 minutes)")
        return v

class CalculationResponse(BaseModel):
    """Response model for penalty calculation"""
    request_id: str
    timestamp: str
    input_data: Dict[str, Any]
    calculation_result: Dict[str, Any]
    ai_explanation: Optional[Dict[str, Any]] = None
    notifications_sent: bool = False

@router.post("/calculate", response_model=CalculationResponse)
async def calculate_penalty(request: CalculationRequest):
    """
    Calculate penalty based on delay minutes with AI explanation
    """
    try:
        # Generate unique request ID
        from uuid import uuid4
        request_id = str(uuid4())
        
        # Calculate penalty using business rules
        penalty_result = penalty_calculator.calculate(
            delay_minutes=request.delay_minutes,
            service_type=request.service_type
        )
        
        # Get AI explanation for the decision
        ai_explanation = None
        if penalty_result["penalty_applied"]:
            ai_explanation = decision_engine.explain_penalty(
                delay_minutes=request.delay_minutes,
                penalty_amount=penalty_result["penalty_amount"],
                rule_applied=penalty_result["rule_applied"]
            )
        else:
            ai_explanation = decision_engine.explain_no_penalty(
                delay_minutes=request.delay_minutes
            )
        
        # Prepare response
        response_data = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "input_data": request.dict(),
            "calculation_result": penalty_result,
            "ai_explanation": ai_explanation,
            "notifications_sent": False  # Will be updated when notifications are implemented
        }
        
        return CalculationResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Calculation failed: {str(e)}"
        )

@router.get("/thresholds")
async def get_penalty_thresholds():
    """
    Get current penalty thresholds and amounts
    """
    config = settings.get_penalty_config()
    return {
        "thresholds": config["thresholds"],
        "amounts": config["amounts"],
        "currency": "INR",
        "last_updated": datetime.now().isoformat()
    }

@router.get("/calculate/batch")
async def batch_calculate(
    delays: str = Query(..., description="Comma-separated delay minutes")
):
    """
    Calculate penalties for multiple delays
    """
    try:
        delay_list = [int(d.strip()) for d in delays.split(",")]
        results = []
        
        for delay in delay_list:
            if 0 <= delay <= 1440:
                result = penalty_calculator.calculate(delay_minutes=delay)
                results.append({
                    "delay_minutes": delay,
                    "penalty_amount": result["penalty_amount"],
                    "rule_applied": result["rule_applied"]
                })
        
        return {
            "batch_id": str(datetime.now().timestamp()),
            "total_calculations": len(results),
            "results": results
        }
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid delay values. Please provide comma-separated integers."
        )