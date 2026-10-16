"""
Anomaly Detection Module
Identifies unusual patterns in business data using Isolation Forest.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from typing import Dict, Any, List
from datetime import datetime


class AnomalyDetector:
    """Anomaly detection using Isolation Forest."""

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None

    def prepare_features(self, df: pd.DataFrame, metric: str = 'total_amount') -> pd.DataFrame:
        """Prepare features for anomaly detection."""
        df = df.copy()

        # Ensure date is datetime
        if 'sale_date' in df.columns:
            df['sale_date'] = pd.to_datetime(df['sale_date'])
            df['date'] = df['sale_date']
        elif 'expense_date' in df.columns:
            df['expense_date'] = pd.to_datetime(df['expense_date'])
            df['date'] = df['expense_date']
        else:
            df['date'] = pd.to_datetime('now')

        # Extract date features
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_year'] = df['date'].dt.dayofyear

        # Ensure metric column exists
        if metric not in df.columns:
            if metric == 'total_amount' and 'amount' in df.columns:
                df['total_amount'] = df['amount']
            else:
                df[metric] = 0

        # Calculate rolling statistics
        df = df.sort_values('date')
        df['rolling_mean_7d'] = df[metric].rolling(window=7, min_periods=1).mean()
        df['rolling_std_7d'] = df[metric].rolling(window=7, min_periods=1).std()
        df['rolling_mean_30d'] = df[metric].rolling(window=30, min_periods=1).mean()

        # Lag features
        df['lag_1d'] = df[metric].shift(1)
        df['lag_7d'] = df[metric].shift(7)

        # Z-score (number of standard deviations from mean)
        df['z_score'] = (df[metric] - df['rolling_mean_7d']) / (df['rolling_std_7d'] + 1e-8)

        # Fill NaN values
        df = df.fillna(0)

        return df

    def train(self, df: pd.DataFrame, metric: str = 'total_amount', contamination: float = 0.05) -> Dict[str, Any]:
        """Train the anomaly detection model."""
        # Prepare features
        df = self.prepare_features(df, metric)

        # Select feature columns
        feature_cols = [metric, 'rolling_mean_7d', 'rolling_std_7d', 'rolling_mean_30d',
                      'lag_1d', 'lag_7d', 'z_score']
        available_cols = [col for col in feature_cols if col in df.columns]
        self.feature_columns = available_cols

        X = df[available_cols]

        # Handle insufficient data
        if len(X) < 30:
            return {
                'error': 'Insufficient data for training. Need at least 30 records.',
                'status': 'failed'
            }

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train Isolation Forest
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.model.fit(X_scaled)

        # Detect anomalies
        anomaly_labels = self.model.predict(X_scaled)
        anomaly_scores = self.model.score_samples(X_scaled)

        # Count anomalies
        n_anomalies = (anomaly_labels == -1).sum()
        n_normal = (anomaly_labels == 1).sum()

        metrics = {
            'contamination': contamination,
            'anomalies_detected': int(n_anomalies),
            'normal_records': int(n_normal),
            'anomaly_rate': float(n_anomalies / len(X)),
            'training_samples': len(X)
        }

        return metrics

    def predict(self, df: pd.DataFrame, metric: str = 'total_amount') -> pd.DataFrame:
        """Detect anomalies in data."""
        if self.model is None or self.feature_columns is None:
            raise ValueError("Model not trained. Call train() first.")

        # Prepare features
        df = self.prepare_features(df, metric)

        # Select features
        X = df[self.feature_columns]

        # Scale and predict
        X_scaled = self.scaler.transform(X)
        anomaly_labels = self.model.predict(X_scaled)
        anomaly_scores = self.model.score_samples(X_scaled)

        # Add anomaly information to dataframe
        df['is_anomaly'] = anomaly_labels == -1
        df['anomaly_score'] = anomaly_scores
        df['anomaly_severity'] = pd.cut(
            df['anomaly_score'],
            bins=[-1, -0.7, -0.4, 0],
            labels=['critical', 'high', 'low']
        )

        return df

    def get_anomalies(self, df: pd.DataFrame, metric: str = 'total_amount') -> List[Dict[str, Any]]:
        """Get list of detected anomalies with details."""
        if self.model is None or self.feature_columns is None:
            raise ValueError("Model not trained. Call train() first.")

        # Predict anomalies
        df = self.predict(df, metric)

        # Filter anomalies
        anomalies_df = df[df['is_anomaly']]

        anomalies = []
        for _, row in anomalies_df.iterrows():
            anomalies.append({
                'date': str(row['date']),
                'value': float(row[metric]),
                'anomaly_score': float(row['anomaly_score']),
                'severity': str(row['anomaly_severity']),
                'rolling_mean': float(row['rolling_mean_7d']),
                'z_score': float(row['z_score'])
            })

        return anomalies

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
