# Summary of Required Input Data from Backend for ML Model

Based on the Convex schema and the requirements outlined in the first sprint plan, the ML model requires the following data from the backend to calculate coating health scores and make degradation forecasts:

## Required Data Fields

### 1. Coating Record Data (from `coatingRecords` table)
- `coatingRecordId`: Unique identifier for the coating application
- `customerId`: Reference to customer (for personalization)
- `vehicleInfo`: Vehicle details (year, make, model, VIN)
- `coatingProductId`: Reference to specific coating product used
- `applicationDate`: Timestamp when coating was applied (Unix milliseconds)
- `warrantyEndDate`: Optional warranty expiration timestamp
- `zipCode`: Location for weather data lookup

### 2. Coating Product Data (from `coatings` table)
- `productId`: External product ID from manufacturer or vector store
- Used to retrieve coating chemistry characteristics from vector store
- Affects degradation rates (different products have different UV resistance)

### 3. Weather Data (from `weatherData` table)
- `zipCode`: Must match coating record's zipCode
- `date`: Timestamp at start of day (UTC) in Unix milliseconds
- `uvIndex`: UV index value (0-15+)
- `rainfall`: Daily rainfall in millimeters
- `temperatureAvg`: Average daily temperature in Celsius

### 4. Data Frequency and Historical Requirements
- **Minimum historical data**: 30 days of weather data for initial model training
- **Optimal historical data**: 1-2 years for capturing seasonal patterns
- **Update frequency**: Daily weather data updates via cron job
- **Data granularity**: Daily aggregates are sufficient for MVP

## Data Pipeline Requirements

### For Initial Model Training:
1. Historical coating application dates
2. Corresponding historical weather data (UV, rainfall, temperature) for each day since application
3. Coating product information to adjust degradation rates

### For Ongoing Predictions:
1. Current coating record with application date
2. Recent weather data (last 30 days minimum)
3. Forecast or historical average UV exposure for future periods
4. Coating product specifics for chemistry-based adjustments

## Data Format Specifications

### Timestamps:
- Unix milliseconds (as stored in Convex `v.number()`)
- Convert to Python datetime for processing: `datetime.fromtimestamp(ts/1000)`

### UV Index:
- Numerical value (typically 0-15+, can exceed 15 in extreme conditions)
- Primary driver of degradation in the model

### Rainfall:
- Millimeters of precipitation per day
- May have protective effect (washes away contaminants) or negative effect (acid rain, depending on location)

### Temperature:
- Average daily temperature in Celsius
- Affects chemical reaction rates (higher temp = faster degradation)

## Data Quality Requirements

1. **Completeness**: No missing values for required fields in training periods
2. **Consistency**: Uniform units (UV index, mm rainfall, Celsius temperature)
3. **Timeliness**: Weather data updated daily by backend cron
4. **Accuracy**: UV index from reliable weather service (NOAA, OpenWeatherMap, etc.)

## Optional Enhancements for Future Iterations

1. **UV Forecast Data**: For predictive forecasting (could integrate weather forecast APIs)
2. **Extreme Weather Events**: Hail, sandstorms, etc. that may cause physical damage
3. **Humidity Data**: Affects some coating chemistries
4. **Pollution/Air Quality Data**: Particularly relevant in urban environments
5. **Application Quality Metrics**: If available (thickness, uniformity, etc.)

## Example Data Flow

1. Customer purchases ceramic coating via Stripe → Backend creates CoatingRecord
2. Backend stores coating product ID and application timestamp
3. Daily weather cron populates WeatherData table for all ZIP codes
4. ML service queries:
   - Specific CoatingRecord by ID
   - WeatherData for that ZIP code from application date to present
   - Coating product details from coatings table
5. ML service calculates health score and returns to backend for storage/update