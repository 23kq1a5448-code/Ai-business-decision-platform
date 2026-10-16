"""
Sales Prediction Module
Uses historical sales data to predict future sales.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
import os


class SalesPredictor:
    """Sales prediction model using Random Forest."""

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for sales prediction."""
        df = df.copy()

        # Ensure date is datetime
        df['sale_date'] = pd.to_datetime(df['sale_date'])

        # Extract date features
        df['year'] = df['sale_date'].dt.year
        df['month'] = df['sale_date'].dt.month
        df['day'] = df['sale_date'].dt.day
        df['day_of_week'] = df['sale_date'].dt.dayofweek
        df['day_of_year'] = df['sale_date'].dt.dayofyear
        df['week_of_year'] = df['sale_date'].dt.isocalendar().week.astype(int)

        # Calculate rolling averages (7-day, 30-day)
        df = df.sort_values('sale_date')
        df['rolling_7d'] = df['total_amount'].rolling(window=7, min_periods=1).mean()
        df['rolling_30d'] = df['total_amount'].rolling(window=30, min_periods=1).mean()

        # Lag features
        df['lag_1d'] = df['total_amount'].shift(1)
        df['lag_7d'] = df['total_amount'].shift(7)

        # Fill NaN values
        df = df.fillna(0)

        return df

    def train(self, df: pd.DataFrame, target_column: str = 'total_amount') -> Dict[str, Any]:
        """Train the sales prediction model."""
        # Prepare features
        df = self.prepare_features(df)

        # Select feature columns
        feature_cols = ['year', 'month', 'day', 'day_of_week', 'day_of_year', 'week_of_year',
                      'rolling_7d', 'rolling_30d', 'lag_1d', 'lag_7d']

        # Remove columns that might not exist
        available_cols = [col for col in feature_cols if col in df.columns]
        self.feature_columns = available_cols

        X = df[available_cols]
        y = df[target_column]

        # Handle insufficient data
        if len(X) < 30:
            return {
                'error': 'Insufficient data for training. Need at least 30 records.',
                'status': 'failed'
            }

        # Split data chronologically
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train_scaled, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_scaled)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        metrics = {
            'MAE': float(mae),
            'RMSE': float(rmse),
            'R2': float(r2),
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }

        return metrics

    def predict(self, df: pd.DataFrame, days_ahead: int = 30) -> pd.DataFrame:
        """Predict sales for future dates."""
        if self.model is None or self.feature_columns is None:
            raise ValueError("Model not trained. Call train() first.")

        # Prepare features
        df = self.prepare_features(df)

        # Get the last date
        last_date = df['sale_date'].max()

        # Generate future dates
        future_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]

        predictions = []
        for future_date in future_dates:
            # Create feature row for future date
            row = {
                'year': future_date.year,
                'month': future_date.month,
                'day': future_date.day,
                'day_of_week': future_date.weekday(),
                'day_of_year': future_date.timetuple().tm_yday,
                'week_of_year': future_date.isocalendar()[1],
                'rolling_7d': df['total_amount'].tail(7).mean(),
                'rolling_30d': df['total_amount'].tail(30).mean(),
                'lag_1d': df['total_amount'].iloc[-1],
                'lag_7d': df['total_amount'].tail(7).mean()
            }

            # Select only available features
            feature_row = [row[col] for col in self.feature_columns]

            # Scale and predict
            feature_row_scaled = self.scaler.transform([feature_row])
            prediction = self.model.predict(feature_row_scaled)[0]

            predictions.append({
                'date': future_date,
                'predicted_sales': max(0, prediction)  # Ensure non-negative
            })

        return pd.DataFrame(predictions)

    def save_model(self, path: str):
        """Save the trained model and scaler."""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }
        joblib.dump(model_data, path)

    def load_model(self, path: str):
        """Load a trained model and scaler."""
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
