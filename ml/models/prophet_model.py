"""
Prophet model for coating degradation forecasting.
Takes UV exposure as input and outputs degradation over time.
"""

import pandas as pd
from prophet import Prophet
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DegradationProphetModel:
    """
    Prophet-based model for predicting coating degradation based on UV exposure.
    """

    def __init__(self, 
                 yearly_seasonality: bool = True,
                 weekly_seasonality: bool = False,
                 daily_seasonality: bool = False):
        """
        Initialize the Prophet model.
        
        Args:
            yearly_seasonality: Whether to include yearly seasonality
            weekly_seasonality: Whether to include weekly seasonality
            daily_seasonality: Whether to include daily seasonality
        """
        self.model = Prophet(
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=daily_seasonality
        )
        # UV exposure will be added as a regressor
        self.is_fitted = False
        
    def add_uv_regressor(self, uv_column_name: str = 'uv_exposure'):
        """
        Add UV exposure as a regressor to the model.
        
        Args:
            uv_column_name: Name of the UV exposure column in the training data
        """
        self.model.add_regressor(uv_column_name)
        self.uv_column_name = uv_column_name
        
    def fit(self, 
            df: pd.DataFrame,
            uv_column_name: str = 'uv_exposure') -> None:
        """
        Fit the Prophet model on historical data.
        
        Args:
            df: DataFrame with columns ['ds', 'y', uv_column_name]
                ds: datestamp
                y: degradation value (0-100, where 0 is no degradation, 100 is fully degraded)
                uv_column_name: UV exposure values
        """
        # Ensure required columns exist
        required_cols = ['ds', 'y', uv_column_name]
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            raise ValueError(f"Missing required columns: {missing}")
            
        # Add UV regressor if not already added
        if not hasattr(self, 'uv_column_name'):
            self.add_uv_regressor(uv_column_name)
            
        # Fit the model
        self.model.fit(df)
        self.is_fitted = True
        logger.info("Prophet model fitted successfully")
        
    def predict(self, 
                future_df: pd.DataFrame,
                uv_column_name: str = 'uv_exposure') -> pd.DataFrame:
        """
        Make predictions for future degradation.
        
        Args:
            future_df: DataFrame with future dates and UV exposure values
                      Must contain 'ds' and uv_column_name columns
            uv_column_name: Name of the UV exposure column
            
        Returns:
            DataFrame with forecast including 'ds', 'yhat', 'yhat_lower', 'yhat_upper'
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before making predictions")
            
        # Ensure required columns exist
        if 'ds' not in future_df.columns:
            raise ValueError("Future dataframe must contain 'ds' column")
        if uv_column_name not in future_df.columns:
            raise ValueError(f"Future dataframe must contain '{uv_column_name}' column")
            
        # Make forecast
        forecast = self.model.predict(future_df)
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        
    def forecast_degradation(self, 
                            start_date: str,
                            periods: int,
                            freq: str = 'D',
                            uv_forecast: Optional[pd.Series] = None) -> pd.DataFrame:
        """
        Generate a degradation forecast for future periods.
        
        Args:
            start_date: Start date for forecast (string parsable by pandas)
            periods: Number of periods to forecast
            freq: Frequency string (e.g., 'D' for day, 'W' for week)
            uv_forecast: Series of UV exposure values for each period (optional)
            
        Returns:
            Forecast DataFrame
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before making predictions")
            
        # Create future dataframe
        future_dates = pd.date_range(start=start_date, periods=periods, freq=freq)
        future_df = pd.DataFrame({'ds': future_dates})
        
        # Add UV forecast if provided, otherwise use average or default
        if uv_forecast is not None:
            if len(uv_forecast) != periods:
                raise ValueError("Length of uv_forecast must match periods")
            future_df[self.uv_column_name] = uv_forecast.values
        else:
            # Use a default UV value (could be improved with historical average)
            logger.warning("No UV forecast provided, using default value of 5.0")
            future_df[self.uv_column_name] = 5.0
            
        return self.predict(future_df, self.uv_column_name)


def create_sample_model() -> DegradationProphetModel:
    """
    Create and return a sample model for demonstration purposes.
    In practice, this would be trained on real data.
    """
    model = DegradationProphetModel()
    model.add_uv_regressor('uv_exposure')
    return model