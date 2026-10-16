"""
Customer Churn Prediction Module
Identifies customers at risk of leaving.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib
from typing import Dict, Any
from datetime import datetime


class ChurnPredictor:
    """Customer churn prediction model."""

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for churn prediction."""
        df = df.copy()

        # RFM (Recency, Frequency, Monetary) features
        if 'last_purchase_date' in df.columns:
            df['last_purchase_date'] = pd.to_datetime(df['last_purchase_date'])
            df['recency_days'] = (datetime.now() - df['last_purchase_date']).dt.days
        else:
            df['recency_days'] = 0

        if 'total_orders' in df.columns:
            df['frequency'] = df['total_orders']
        else:
            df['frequency'] = 0

        if 'total_spending' in df.columns:
            df['monetary'] = df['total_spending']
        else:
            df['monetary'] = 0

        # Average order value
        if df['frequency'] > 0:
            df['avg_order_value'] = df['monetary'] / df['frequency']
        else:
            df['avg_order_value'] = 0

        # Customer age
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['customer_age_days'] = (datetime.now() - df['created_at']).dt.days
        else:
            df['customer_age_days'] = 0

        # Fill NaN values
        df = df.fillna(0)

        return df

    def train(self, df: pd.DataFrame, target_column: str = 'churn') -> Dict[str, Any]:
        """Train the churn prediction model."""
        # Prepare features
        df = self.prepare_features(df)

        # Select feature columns
        feature_cols = ['recency_days', 'frequency', 'monetary', 'avg_order_value', 'customer_age_days']
        available_cols = [col for col in feature_cols if col in df.columns]
        self.feature_columns = available_cols

        X = df[available_cols]

        # Simulate churn labels for demo (in production, use actual churn data)
        # Higher recency and lower frequency increases churn risk
        if target_column not in df.columns:
            df['churn'] = (
                (df['recency_days'] > 90) & (df['frequency'] < 5)
            ).astype(int)

        y = df['churn']

        # Handle insufficient data
        if len(X) < 20:
            return {
                'error': 'Insufficient data for training. Need at least 20 records.',
                'status': 'failed'
            }

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        self.model.fit(X_train_scaled, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]

        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_pred_proba) if len(np.unique(y_test)) > 1 else 0.5
        accuracy = accuracy_score(y_test, y_pred)

        metrics = {
            'precision': float(precision),
            'recall': float(recall),
            'F1': float(f1),
            'ROC-AUC': float(roc_auc),
            'accuracy': float(accuracy),
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }

        return metrics

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict churn probability for customers."""
        if self.model is None or self.feature_columns is None:
            raise ValueError("Model not trained. Call train() first.")

        # Prepare features
        df = self.prepare_features(df)

        # Select features
        X = df[self.feature_columns]

        # Scale and predict
        X_scaled = self.scaler.transform(X)
        churn_proba = self.model.predict_proba(X_scaled)[:, 1]

        # Add predictions to dataframe
        df['churn_probability'] = churn_proba

        # Categorize risk
        df['churn_risk'] = pd.cut(
            df['churn_probability'],
            bins=[0, 0.3, 0.7, 1.0],
            labels=['low', 'medium', 'high']
        )

        return df

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
