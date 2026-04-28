"""
Coating Health Score calculation and maintenance trigger logic.
Converts degradation predictions to a 0-100 health score.
"""

from typing import Optional, Dict, Any
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class HealthScoreCalculator:
    """
    Calculates coating health score (0-100) from degradation predictions.
    Implements maintenance trigger logic (score < 65).
    """
    
    def __init__(self, 
                 degradation_thresholds: Optional[Dict[str, float]] = None):
        """
        Initialize the health score calculator.
        
        Args:
            degradation_thresholds: Custom thresholds for degradation levels
                Keys: 'excellent', 'good', 'fair', 'poor', 'critical'
                Values: Maximum degradation for each level (0-100 scale)
        """
        # Default thresholds: degradation 0-100 -> health score 100-0
        # These can be adjusted based on coating chemistry and product specs
        self.degradation_thresholds = degradation_thresholds or {
            'excellent': 10,   # 0-10% degradation -> 90-100 health
            'good': 25,        # 10-25% degradation -> 75-90 health
            'fair': 40,        # 25-40% degradation -> 60-75 health
            'poor': 60,        # 40-60% degradation -> 40-60 health
            'critical': 80     # 60-80% degradation -> 20-40 health
            # >80% degradation -> 0-20 health (needs immediate attention)
        }
        
        # Maintenance trigger threshold (health score below this needs maintenance)
        self.maintenance_threshold = 65
        
    def degradation_to_health_score(self, 
                                   degradation: float) -> float:
        """
        Convert degradation percentage to health score (0-100).
        
        Args:
            degradation: Degradation percentage (0-100, where 0 is new, 100 is fully degraded)
            
        Returns:
            Health score (0-100, where 100 is perfect condition, 0 is failed)
        """
        # Clamp degradation to valid range
        degradation = max(0.0, min(100.0, degradation))
        
        # Simple linear inversion: health = 100 - degradation
        # This can be made more sophisticated with non-linear mapping if needed
        health_score = 100.0 - degradation
        
        return max(0.0, min(100.0, health_score))
        
    def get_health_grade(self, health_score: float) -> str:
        """
        Convert health score to a letter grade or category.
        
        Args:
            health_score: Health score (0-100)
            
        Returns:
            Health grade/category string
        """
        if health_score >= 90:
            return "Excellent"
        elif health_score >= 75:
            return "Good"
        elif health_score >= 60:
            return "Fair"
        elif health_score >= 40:
            return "Poor"
        else:
            return "Critical"
            
    def needs_maintenance(self, health_score: float) -> bool:
        """
        Determine if maintenance is needed based on health score.
        
        Args:
            health_score: Health score (0-100)
            
        Returns:
            True if maintenance is needed (score < 65), False otherwise
        """
        return health_score < self.maintenance_threshold
        
    def calculate_health_score_from_prediction(self, 
                                              prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate health score from a Prophet prediction object.
        
        Args:
            prediction: Dictionary containing Prophet forecast output
                       Expected to have 'yhat' key with degradation prediction
                       
        Returns:
            Dictionary with health score, grade, and maintenance flag
        """
        # Extract degradation prediction (yhat is the predicted degradation)
        degradation = prediction.get('yhat', 0.0)
        
        # Calculate health score
        health_score = self.degradation_to_health_score(degradation)
        
        # Get health grade
        grade = self.get_health_grade(health_score)
        
        # Check if maintenance is needed
        needs_maintenance = self.needs_maintenance(health_score)
        
        return {
            'degradation_prediction': degradation,
            'health_score': health_score,
            'health_grade': grade,
            'needs_maintenance': needs_maintenance,
            'maintenance_threshold': self.maintenance_threshold,
            'confidence_interval': {
                'lower': self.degradation_to_health_score(prediction.get('yhat_upper', 100.0)),
                'upper': self.degradation_to_health_score(prediction.get('yhat_lower', 0.0))
            } if 'yhat_upper' in prediction and 'yhat_lower' in prediction else None
        }
        
    def batch_calculate_health_scores(self, 
                                     predictions: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate health scores for a batch of predictions.
        
        Args:
            predictions: DataFrame with Prophet forecast output (ds, yhat, yhat_lower, yhat_upper)
            
        Returns:
            DataFrame with added health score columns
        """
        df = predictions.copy()
        
        # Calculate health score from degradation prediction
        df['health_score'] = 100.0 - df['yhat']
        df['health_score'] = df['health_score'].clip(0.0, 100.0)
        
        # Calculate health grade
        df['health_grade'] = pd.cut(df['health_score'], 
                                   bins=[0, 40, 60, 75, 90, 100],
                                   labels=['Critical', 'Poor', 'Fair', 'Good', 'Excellent'],
                                   right=False)
                                   
        # Maintenance flag
        df['needs_maintenance'] = df['health_score'] < self.maintenance_threshold
        
        # Confidence intervals for health score (inverted from degradation CI)
        if 'yhat_lower' in df.columns and 'yhat_upper' in df.columns:
            df['health_score_lower'] = 100.0 - df['yhat_upper']
            df['health_score_upper'] = 100.0 - df['yhat_lower']
            df['health_score_lower'] = df['health_score_lower'].clip(0.0, 100.0)
            df['health_score_upper'] = df['health_score_upper'].clip(0.0, 100.0)
            
        return df


def create_health_score_calculator() -> HealthScoreCalculator:
    """
    Factory function to create a health score calculator with default settings.
    """
    return HealthScoreCalculator()


if __name__ == "__main__":
    # Example usage
    calculator = HealthScoreCalculator()
    
    # Test degradation to health score conversion
    test_degradations = [0, 10, 25, 40, 60, 80, 100]
    print("Degradation -> Health Score:")
    for deg in test_degradations:
        health = calculator.degradation_to_health_score(deg)
        grade = calculator.get_health_grade(health)
        maint = calculator.needs_maintenance(health)
        print(f"  {deg:3d}% degradation -> {health:3.0f} health ({grade}) - Maintenance: {maint}")