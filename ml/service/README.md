# CeraShield ML Service

This service provides the machine learning models for calculating ceramic coating health scores.

## Overview
The ML service wraps Prophet and scikit-learn models to provide health score predictions based on:
- UV exposure (primary driver of degradation)
- Rainfall and temperature (secondary factors)
- Coating chemistry (from product data)
- Time since application

## API Endpoints

### POST /health-score
Calculate the current health score for a coating record.

#### Request Body
```json
{
  "coatingRecordId": "string",
  "applicationDate": 1234567890123,
  "coatingProduct": {
    "id": "string",
    "name": "string",
    "productId": "string",
    "uvResistance": 0.8,
    "expectedLifespanMonths": 24,
    "hydrophobicRating": 0.9
  },
  "weatherData": [
    {
      "date": 1234567890123,
      "uvIndex": 7.2,
      "rainfall": 0.0,
      "temperatureAvg": 25.5
    }
  ]
}
```

#### Response
```json
{
  "coating_record_id": "string",
  "timestamp": "ISO 8601 string",
  "current_health_score": {
    "score": 85,
    "grade": "Good",
    "degradation_percentage": 15,
    "needs_maintenance": false,
    "maintenance_threshold": 65,
    "confidence_interval": {
      "lower": 80,
      "upper": 90
    }
  },
  "forecast": null,
  "metadata": {
    "model_version": "prophet-mvp-v1",
    "last_updated": "ISO 8601 string",
    "data_points_used": 30,
    "days_since_application": 180
  }
}
```

## Deployment

### Option 1: Direct Execution (for development)
```bash
pip install -r requirements.txt
python ml/service/main.py
```

### Option 2: Docker
```bash
docker build -t cerashield-ml-service .
docker run -p 8000:8000 cerashield-ml-service
```

### Option 3: Hugging Face Spaces
1. Create a new Space with Docker SDK
2. Add the files from this directory
3. Set the port to 7860 (HF Spaces default)
4. The service will be available at your-space-name.hf.space

## Environment Variables
- `PORT`: Port to run the service on (default: 8000)

## Model Information
- **Primary Model**: Prophet with UV exposure as regressor
- **Health Score Calculation**: Linear inversion of degradation (100 - degradation %)
- **Maintenance Trigger**: Health score < 65