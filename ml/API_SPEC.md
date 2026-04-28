# Health Score API Specification

## Overview
This document specifies the API endpoints for the CeraShield ML service that provides coating health score predictions and maintenance recommendations.

## Base URL
`https://api.cerashield-os.com/ml/v1`

## Authentication
All endpoints require API key authentication via header:
```
Authorization: Bearer <api_key>
```

## Endpoints

### 1. Get Current Health Score
Retrieve the current health score for a specific coating application.

**GET** `/health-score/{coating_record_id}`

#### Parameters
- `coating_record_id` (path, required): Unique identifier for the coating record

#### Query Parameters
- `include_forecast` (optional, boolean): Whether to include future degradation forecast (default: false)
- `forecast_days` (optional, integer): Number of days to forecast if include_forecast=true (default: 30)

#### Response
```json
{
  "coating_record_id": "string",
  "timestamp": "ISO 8601 datetime string",
  "current_health_score": {
    "score": 0-100,
    "grade": "Excellent|Good|Fair|Poor|Critical",
    "degradation_percentage": 0-100,
    "needs_maintenance": boolean,
    "maintenance_threshold": 65
  },
  "forecast": {
    "enabled": boolean,
    "forecast_days": integer,
    "predictions": [
      {
        "date": "ISO 8601 date string",
        "predicted_health_score": 0-100,
        "health_grade": "Excellent|Good|Fair|Poor|Critical",
        "confidence_interval": {
          "lower": 0-100,
          "upper": 0-100
        }
      }
    ]
  } | null,
  "metadata": {
    "model_version": "string",
    "last_updated": "ISO 8601 datetime string",
    "data_points_used": integer
  }
}
```

#### Error Responses
- `404`: Coating record not found
- `429`: Rate limit exceeded
- `500`: Internal server error
- `503`: Model service unavailable

### 2. Update Health Score with New Weather Data
Trigger a health score recalculation when new weather data is available.

**POST** `/health-score/{coating_record_id}/update`

#### Parameters
- `coating_record_id` (path, required): Unique identifier for the coating record

#### Request Body
```json
{
  "weather_data": [
    {
      "date": "ISO 8601 date string",
      "uv_index": 0-15+,
      "rainfall_mm": 0-1000+,
      "temperature_c": -50 to 60
    }
  ],
  "force_recalculation": boolean (optional, default: false)
}
```

#### Response
Same as GET `/health-score/{coating_record_id}`

### 3. Get Health Score History
Retrieve historical health scores for trend analysis.

**GET** `/health-score/{coating_record_id}/history`

#### Parameters
- `coating_record_id` (path, required): Unique identifier for the coating record

#### Query Parameters
- `start_date` (optional, ISO 8601 date): Start of date range
- `end_date` (optional, ISO 8601 date): End of date range
- `limit` (optional, integer): Maximum number of records to return (default: 100, max: 1000)

#### Response
```json
{
  "coating_record_id": "string",
  "history": [
    {
      "timestamp": "ISO 8601 datetime string",
      "health_score": 0-100,
      "health_grade": "Excellent|Good|Fair|Poor|Critical",
      "degradation_percentage": 0-100,
      "uv_exposure": float,
      "rainfall_mm": float,
      "temperature_c": float
    }
  ],
  "summary": {
    "average_health_score": 0-100,
    "min_health_score": 0-100,
    "max_health_score": 0-100,
    "trend": "improving|stable|declining",
    "days_since_application": integer
  }
}
```

### 4. Get Maintenance Recommendations
Get specific maintenance recommendations based on health score and trends.

**GET** `/health-score/{coating_record_id}/maintenance`

#### Parameters
- `coating_record_id` (path, required): Unique identifier for the coating record

#### Response
```json
{
  "coating_record_id": "string",
  "timestamp": "ISO 8601 datetime string",
  "current_health_score": 0-100,
  "maintenance_recommended": boolean,
  "urgency": "low|medium|high|critical",
  "recommended_actions": [
    {
      "action": "string",
      "description": "string",
      "priority": "low|medium|high",
      "estimated_cost": "string (optional)",
      "timeframe": "string (e.g., 'within 30 days')"
    }
  ],
  "next_maintenance_date": "ISO 8601 date string (optional)",
  "predicted_health_at_next_maintenance": 0-100 (optional)
}
```

## Data Models

### Health Score Object
- `score`: Numerical health score (0-100)
- `grade`: Categorical grade based on score thresholds
- `degradation_percentage`: Inverse of health score (0-100)
- `needs_maintenance`: Boolean indicating if score < maintenance threshold (65)
- `maintenance_threshold`: The threshold value (fixed at 65 for MVP)

### Forecast Prediction Object
- `date`: Forecast date
- `predicted_health_score`: Expected health score on that date
- `health_grade`: Grade corresponding to predicted score
- `confidence_interval`: Lower and upper bounds of prediction confidence

## Rate Limiting
- Default: 100 requests per minute per API key
- Burst: 20 requests per second
- Exceeding limits returns HTTP 429

## Versioning
API version is specified in the URL path (`/v1/`). Breaking changes will increment the version number.

## Error Format
All errors return JSON in the following format:
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object (optional)"
  }
}
```

## Implementation Notes for Backend
1. The ML service should be deployed as a separate microservice
2. Caching layer recommended for recent health scores
3. Model predictions should be asynchronous for non-real-time updates
4. Health score calculations should use the most recent weather data available
5. Forecasts should use historical averages or weather forecasts for future UV exposure