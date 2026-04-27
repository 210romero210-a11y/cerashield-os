# ML Service for CeraShield OS
# FastAPI service that wraps the Prophet/scikit-learn models for health score calculation

"""
ML Service for CeraShield OS
Provides HTTP API for coating health score calculation using Prophet/scikit-learn models
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
import sys
import os
from datetime import datetime
import logging

# Add the ml directory to path so we can import our models
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.prophet_model import DegradationProphetModel
from health_score_calculator import HealthScoreCalculator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CeraShield ML Service",
    description="API for calculating ceramic coating health scores using ML models",
    version="1.0.0"
)

# Initialize components
prophet_model = DegradationProphetModel()
prophet_model.add_uv_regressor('uv_exposure')
health_calculator = HealthScoreCalculator()

# Data models
class WeatherDataPoint(BaseModel):
    date: int = Field(..., description="Unix milliseconds timestamp at start of day (UTC)")
    uvIndex: float = Field(..., ge=0, description="UV index value")
    rainfall: float = Field(..., ge=0, description="Daily rainfall in millimeters")
    temperatureAvg: float = Field(..., description="Average daily temperature in Celsius")

class CoatingProduct(BaseModel):
    id: str = Field(..., description="Internal coating product ID")
    name: str = Field(..., description="Coating product name")
    productId: str = Field(..., description="External product ID from manufacturer")
    uvResistance: Optional[float] = Field(None, ge=0, le=1, description="UV resistance rating (0-1)")
    expectedLifespanMonths: Optional[float] = Field(None, gt=0, description="Expected lifespan in months")
    hydrophobicRating: Optional[float] = Field(None, ge=0, le=1, description="Hydrophobic rating (0-1)")

class HealthScoreRequest(BaseModel):
    coatingRecordId: str = Field(..., description="Unique identifier for the coating record")
    applicationDate: int = Field(..., description="Unix milliseconds timestamp when coating was applied")
    coatingProduct: CoatingProduct
    weatherData: List[WeatherDataPoint] = Field(..., min_items=1, description="Historical weather data")

class HealthScoreResponse(BaseModel):
    coating_record_id: str
    timestamp: str = Field(..., description="ISO 8601 timestamp of calculation")
    current_health_score: Dict[str, Any]
    forecast: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any]

# Helper functions
def prepare_prophet_input(weather_data: List[WeatherDataPoint], application_date: int) -> Dict[str, Any]:
    """
    Prepare input data for the Prophet model.
    
    Args:
        weather_data: List of historical weather data points
        application_date: Unix milliseconds when coating was applied
        
    Returns:
        Dictionary with data formatted for Prophet model
    """
    # Convert to pandas DataFrame
    import pandas as pd
    
    # Create dataframe with date and UV exposure
    data = []
    for wp in weather_data:
        data.append({
            'ds': datetime.fromtimestamp(wp.date / 1000),  # Convert ms to seconds
            'uv_exposure': wp.uvIndex
        })
    
    df = pd.DataFrame(data)
    
    # For MVP, we'll use a simple approach:
    # Since we don't have historical degradation data to train on,
    # we'll use the Prophet model to predict future degradation based on UV trends
    # In a real system, we would have historical degradation measurements to train the model
    
    return {
        'historical_df': df,
        'application_date': application_date
    }

def predict_degradation_with_prophet(weather_data: List[WeatherDataPoint], application_date: int) -> float:
    """
    Predict degradation using the Prophet model.
    
    For MVP, since we don't have historical degradation measurements to train on,
    we'll use a simplified approach:
    1. Use UV exposure as the primary driver
    2. Apply a simple degradation model based on UV and time
    3. In the future, this would be replaced with a properly trained Prophet model
    
    Args:
        weather_data: List of historical weather data points
        application_date: Unix milliseconds when coating was applied
        
    Returns:
        Predicted degradation percentage (0-100)
    """
    # For MVP implementation, we'll use a simple heuristic
    # In a production system, this would use a properly trained Prophet model
    
    if not weather_data:
        return 0.0
    
    # Calculate days since application
    now = datetime.now().timestamp() * 1000  # Current time in milliseconds
    days_since_application = (now - application_date) / (1000 * 60 * 60 * 24)
    
    # Calculate average UV exposure
    avg_uv = sum(wp.uvIndex for wp in weather_data) / len(weather_data)
    
    # Simple degradation model:
    # Base degradation: 0.05% per day (from time alone)
    # UV amplification: 0.3% per day per UV index point
    # This is a simplified model - in reality would be calibrated to specific coating chemistry
    time_degradation = 0.05 * days_since_application
    uv_degradation = 0.3 * avg_uv * days_since_application / 365.0  # UV effect annualized
    
    # Apply coating-specific modifiers if available
    # For now, we'll use a simple baseline
    
    total_degradation = time_degradation + uv_degradation
    
    # Clamp to reasonable range (0-100%)
    return max(0.0, min(100.0, total_degradation))

# API Endpoints
@app.post("/health-score", response_model=HealthScoreResponse)
async def calculate_health_score(request: HealthScoreRequest):
    """
    Calculate the current health score for a coating record.
    
    This endpoint:
    1. Takes coating record info, product details, and historical weather data
    2. Uses the ML model to predict degradation
    3. Converts degradation to health score (0-100)
    4. Returns health score, grade, and maintenance flag
    """
    try:
        logger.info(f"Calculating health score for coating record {request.coatingRecordId}")
        
        # Predict degradation using our model
        degradation_prediction = predict_degradation_with_prophet(
            request.weatherData,
            request.applicationDate
        )
        
        # Calculate health score from degradation
        health_score_result = health_calculator.calculate_health_score_from_prediction({
            'yhat': degradation_prediction
        })
        
        # Build response
        response = HealthScoreResponse(
            coating_record_id=request.coatingRecordId,
            timestamp=datetime.now().isoformat(),
            current_health_score={
                "score": health_score_result["health_score"],
                "grade": health_score_result["health_grade"],
                "degradation_percentage": health_score_result["degradation_prediction"],
                "needs_maintenance": health_score_result["needs_maintenance"],
                "maintenance_threshold": health_score_result["maintenance_threshold"],
                "confidence_interval": health_score_result.get("confidence_interval")
            },
            # For MVP, we're not implementing forecast yet
            # In a full implementation, we would forecast future degradation
            forecast=None,
            metadata={
                "model_version": "prophet-mvp-v1",
                "last_updated": datetime.now().isoformat(),
                "data_points_used": len(request.weatherData),
                "days_since_application": (datetime.now().timestamp() * 1000 - request.applicationDate) / (1000 * 60 * 60 * 24)
            }
        )
        
        logger.info(f"Health score calculated: {response.current_health_score['score']}")
        return response
        
    except Exception as e:
        logger.error(f"Error calculating health score: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate health score: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for the ML service."""
    return {
        "status": "healthy",
        "service": "CeraShield ML Service",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Get port from environment or default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)