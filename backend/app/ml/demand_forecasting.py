"""
Demand Forecasting Module
Predicts product demand for inventory planning.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta
from typing import Dict, Any
import warnings
warnings.filterwarnings('ignore')


class DemandForecaster:
    """Product demand forecasting model."""

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for demand forecasting."""
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
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)

        # Group by product and date
        if 'product_id' in df.columns:
            df['quantity'] = df.groupby(['product_id', 'sale_date'])['quantity'].transform('sum')

        # Calculate rolling averages
        df = df.sort_values(['product_id', 'sale_date'])
        df['rolling_7d'] = df.groupby('product_id')['quantity'].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean()
        )
        df['rolling_30d'] = df.groupby('product_id')['quantity'].transform(
            lambda x: x.rolling(window=30, min_periods=1).mean()
        )

        # Lag features
        df['lag_1d'] = df.groupby('product_id')['quantity'].shift(1)
        df['lag_7d'] = df.groupby('product_id')['quantity'].shift(7)

        # Fill NaN values
        df = df.fillna(0)

        return df

    def train(self, df: pd.DataFrame, target_column: str = 'quantity') -> Dict[str, Any]:
        """Train the demand forecasting model."""
        # Prepare features
        df = self.prepare_features(df)

        # Select feature columns
        feature_cols = ['year', 'month', 'day', 'day_of_week', 'day_of_year', 'week_of_year',
                      'is_weekend', 'rolling_7d', 'rolling_30d', 'lag_1d', 'lag_7d']
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

        # Calculate MAPE only if no zero values
        if (y_test != 0).all():
            mape = mean_absolute_percentage_error(y_test, y_pred)
        else:
            mape = 0.0

        metrics = {
            'MAE': float(mae),
            'RMSE': float(rmse),
            'MAPE': float(mape),
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }

        return metrics

    def predict(self, df: pd.DataFrame, days_ahead: int = 30, safety_stock_multiplier: float = 1.5) -> pd.DataFrame:
        """Predict demand for products."""
        if self.model is None or self.feature_columns is None:
            raise ValueError("Model not trained. Call train() first.")

        # Prepare features
        df = self.prepare_features(df)

        # Get unique products
        if 'product_id' in df.columns:
            products = df['product_id'].unique()
        else:
            products = [0]  # Single product

        predictions = []
        last_date = df['sale_date'].max()

        for product_id in products:
            product_df = df[df['product_id'] == product_id] if 'product_id' in df.columns else df

            # Generate future dates
            future_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]

            for future_date in future_dates:
                # Create feature row
                row = {
                    'year': future_date.year,
                    'month': future_date.month,
                    'day': future_date.day,
                    'day_of_week': future_date.weekday(),
                    'day_of_year': future_date.timetuple().tm_yday,
                    'week_of_year': future_date.isocalendar()[1],
                    'is_weekend': 1 if future_date.weekday() >= 5 else 0,
                    'rolling_7d': product_df['quantity'].tail(7).mean(),
                    'rolling_30d': product_df['quantity'].tail(30).mean(),
                    'lag_1d': product_df['quantity'].iloc[-1],
                    'lag_7d': product_df['quantity'].tail(7).mean()
                }

                # Select only available features
                feature_row = [row[col] for col in self.feature_columns]

                # Scale and predict
                feature_row_scaled = self.scaler.transform([feature_row])
                prediction = self.model.predict(feature_row_scaled)[0]

                # Calculate suggested reorder (forecast + safety stock)
                current_stock = product_df['stock_quantity'].iloc[-1] if 'stock_quantity' in product_df.columns else 0
                suggested_reorder = max(0, int(prediction * safety_stock_multiplier - current_stock))

                predictions.append({
                    'product_id': product_id,
                    'date': future_date,
                    'predicted_demand': max(0, int(prediction)),
                    'suggested_reorder': suggested_reorder
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
