# ML Service Deployment Plan for CeraShield OS

## Overview
This document outlines the plan for deploying the Python ML models (Prophet/scikit-learn) as a service that can be called from the Convex backend.

## Recommended Approach: FastAPI Microservice
For the MVP, we recommend deploying the ML models as a lightweight FastAPI service. This approach:
- Keeps ML code in Python (no need to rewrite in TypeScript)
- Provides a clean HTTP API that Convex can call
- Is easy to deploy and scale
- Allows for independent versioning of ML models

## Alternative: Child Process (for initial testing only)
For very early testing before setting up the service, we could call the ML models directly from Convex actions using a child process. However, this is:
- Less efficient (spawns a new process for each call)
- Harder to manage dependencies
- Not suitable for production
- Only recommended for initial proof-of-concept

## FastAPI Service Structure

```
ml/service/
├── main.py              # FastAPI app entry point
├── model_loader.py      # Load and manage ML models
├── health_calculator.py # Health score calculation (adapted from existing)
├── data_preprocessor.py # Prepare data for ML models
├── requirements.txt     # Python dependencies
└── Dockerfile           # Optional: for containerization
```

### main.py
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
from model_loader import ModelLoader
from data_preprocessor import prepare_ml_input
from health_calculator import HealthScoreCalculator

app = FastAPI(title="CeraShield ML Service", version="1.0.0")

# Initialize components
model_loader = ModelLoader()
health_calculator = HealthScoreCalculator()

class WeatherDataPoint(BaseModel):
    date: int  # Unix milliseconds
    uvIndex: float
    rainfall: float
    temperatureAvg: float

class CoatingProduct(BaseModel):
    id: str
    name: str
    productId: str
    uvResistance: Optional[float] = None
    expectedLifespanMonths: Optional[float] = None
    hydrophobicRating: Optional[float] = None

class HealthScoreRequest(BaseModel):
    coatingRecordId: str
    applicationDate: int  # Unix milliseconds
    coatingProduct: CoatingProduct
    weatherData: List[WeatherDataPoint]

class HealthScoreResponse(BaseModel):
    coating_record_id: str
    timestamp: str  # ISO 8601
    current_health_score: Dict[str, Any]
    forecast: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any]

@app.post("/health-score", response_model=HealthScoreResponse)
async def calculate_health_score(request: HealthScoreRequest):
    try:
        # Prepare data for ML models
        ml_input = prepare_ml_input(request)
        
        # Get degradation prediction from Prophet model
        degradation_prediction = model_loader.predict_degradation(ml_input)
        
        # Calculate health score
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
            metadata={
                "model_version": "prophet-v1",
                "last_updated": datetime.now().isoformat(),
                "data_points_used": len(request.weatherData)
            }
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### model_loader.py
```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))

from prophet_model import DegradationProphetModel
import pandas as pd
import pickle

class ModelLoader:
    def __init__(self):
        self.prophet_model = None
        self.is_fitted = False
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        # Try to load a pre-trained model
        model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'prophet_model.pkl')
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.prophet_model = pickle.load(f)
            self.is_fitted = True
        else:
            # Create and fit a basic model (in production, this would be trained on real data)
            self.prophet_model = DegradationProphetModel()
            self.prophet_model.add_uv_regressor('uv_exposure')
            # Note: In a real system, we would fit this with historical data
            # For MVP, we'll use a simple baseline or leave unfitted and handle gracefully
            self.is_fitted = False
    
    def predict_degradation(self, ml_input: dict) -> float:
        if not self.is_fitted:
            # Return a simple baseline prediction for MVP
            # In reality, we would want to train on real data or return an error
            # For now, return a degradation based on average UV and time
            avg_uv = sum(day['uvIndex'] for day in ml_input['weatherData']) / len(ml_input['weatherData'])
            days_since = (ml_input['currentDate'] - ml_input['applicationDate']) / (1000 * 60 * 60 * 24)
            # Simple linear degradation: 0.1% per day + 0.5% per UV point
            degradation = min(100, 0.1 * days_since + 0.5 * avg_uv)
            return degradation
        
        # Prepare dataframe for Prophet
        # This would need to be implemented based on the actual ML input format
        # For MVP, we'll use the simple baseline above
        avg_uv = sum(day['uvIndex'] for day in ml_input['weatherData']) / len(ml_input['weatherData'])
        days_since = (ml_input['currentDate'] - ml_input['applicationDate']) / (1000 * 60 * 60 * 24)
        degradation = min(100, 0.1 * days_since + 0.5 * avg_uv)
        return degradation
```

## Deployment Options

### Option 1: Hugging Face Spaces (Free tier available)
- Pros: Free, easy to deploy, comes with GPU option if needed
- Cons: May have cold starts, limited customization
- Good for: MVP and early testing

### Option 2: Railway.app or Render.com
- Pros: Easy deployment, good free tiers, custom domains
- Cons: May require paid plan for production usage
- Good for: MVP to early production

### Option 3: Self-hosted on a VPS (DigitalOcean, AWS Lightsail, etc.)
- Pros: Full control, predictable costs
- Cons: More setup and maintenance required
- Good for: Production when more control is needed

### Option 4: AWS Lambda or Google Cloud Functions
- Pros: Scales to zero, pay-per-use
- Cons: Cold starts, limited execution time, more complex setup
- Good for: Variable traffic patterns

## Integration with Convex

In the Convex `ml.ts` file we created, the `updateHealthScoreForCoatingRecord` action:
1. Gathers all necessary data (coating record, product, weather history)
2. Calls the ML service at `process.env.ML_SERVICE_URL` (to be set in Convex dashboard)
3. Processes the response and stores it in the `healthScores` table
4. Updates the coating record with the latest health score for quick access

## Environment Variables Needed
- `ML_SERVICE_URL`: URL of the deployed FastAPI service
- `ML_SERVICE_TOKEN`: Optional bearer token for authentication
- `WEATHER_API_KEY`: For the weather cron job (to be implemented)

## Next Steps for ML Specialist
1. Set up the FastAPI service structure in `ml/service/`
2. Implement the model loading and prediction logic
3. Create a requirements.txt for the service
4. Deploy to a testing endpoint (e.g., Hugging Face Spaces)
5. Provide the URL to the backend team to set in Convex environment variables

## Immediate Blocker
We need a weather API key for the cron job to fetch real data. For MVP, we can:
1. Use a free tier of OpenWeatherMap or WeatherAPI.com
2. Or continue with mock data until we have a key
3. The backend team should add the API key to Convex environment variables

## Suggested Next Message
After reviewing this plan, the Engineering Manager should:
1. Share this plan with the backend and ML specialists
2. Ask the backend specialist to proceed with setting up the Convex environment variables for the ML service URL
3. Ask the ML specialist to begin implementing the FastAPI service
4. Suggest that the frontend specialist begins setting up the dashboard while waiting for the backend ML integration

The Engineering Manager should then open the next appropriate worktree based on which specialist needs to act next.