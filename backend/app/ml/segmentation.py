"""
Customer Segmentation Module
Uses RFM analysis and K-Means clustering to segment customers.
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import joblib
from typing import Dict, Any
from datetime import datetime


class CustomerSegmenter:
    """Customer segmentation using RFM analysis and K-Means."""

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.cluster_labels = None

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare RFM features for segmentation."""
        df = df.copy()

        # Recency: Days since last purchase
        if 'last_purchase_date' in df.columns:
            df['last_purchase_date'] = pd.to_datetime(df['last_purchase_date'])
            df['recency'] = (datetime.now() - df['last_purchase_date']).dt.days
        else:
            df['recency'] = 0

        # Frequency: Number of purchases
        if 'total_orders' in df.columns:
            df['frequency'] = df['total_orders']
        else:
            df['frequency'] = 0

        # Monetary: Total spending
        if 'total_spending' in df.columns:
            df['monetary'] = df['total_spending']
        else:
            df['monetary'] = 0

        # Average order value
        df['avg_order_value'] = np.where(df['frequency'] > 0, df['monetary'] / df['frequency'], 0)

        # Customer age
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['customer_age'] = (datetime.now() - df['created_at']).dt.days
        else:
            df['customer_age'] = 0

        # Fill NaN values
        df = df.fillna(0)

        return df

    def train(self, df: pd.DataFrame, n_clusters: int = 4) -> Dict[str, Any]:
        """Train the customer segmentation model."""
        # Prepare features
        df = self.prepare_features(df)

        # Select RFM features
        feature_cols = ['recency', 'frequency', 'monetary', 'avg_order_value', 'customer_age']
        available_cols = [col for col in feature_cols if col in df.columns]
        self.feature_columns = available_cols

        X = df[available_cols]

        # Handle insufficient data
        if len(X) < 20:
            return {
                'error': 'Insufficient data for training. Need at least 20 records.',
                'status': 'failed'
            }

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train K-Means
        self.model = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            n_init=10,
            max_iter=300
        )
        self.model.fit(X_scaled)

        # Calculate silhouette score
        silhouette = silhouette_score(X_scaled, self.model.labels_)

        # Calculate cluster statistics
        df['cluster'] = self.model.labels_
        cluster_stats = df.groupby('cluster')[available_cols].mean().to_dict()

        # Assign interpretive labels based on cluster characteristics
        self.cluster_labels = self._assign_cluster_labels(df, available_cols)

        metrics = {
            'silhouette_score': float(silhouette),
            'inertia': float(self.model.inertia_),
            'n_clusters': n_clusters,
            'training_samples': len(X),
            'cluster_stats': cluster_stats,
            'cluster_labels': self.cluster_labels
        }

        return metrics

    def _assign_cluster_labels(self, df: pd.DataFrame, feature_cols: list) -> Dict[int, str]:
        """Assign interpretive labels to clusters based on RFM characteristics."""
        labels = {}
        df['cluster'] = self.model.labels_

        for cluster_id in range(self.model.n_clusters):
            cluster_data = df[df['cluster'] == cluster_id]

            avg_recency = cluster_data['recency'].mean()
            avg_frequency = cluster_data['frequency'].mean()
            avg_monetary = cluster_data['monetary'].mean()

            # Determine segment based on RFM characteristics
            if avg_frequency > 5 and avg_monetary > 1000:
                labels[cluster_id] = 'loyal'
            elif avg_monetary > 2000:
                labels[cluster_id] = 'high-value'
            elif avg_recency < 30 and avg_frequency < 3:
                labels[cluster_id] = 'new'
            elif avg_recency > 90:
                labels[cluster_id] = 'at-risk'
            else:
                labels[cluster_id] = 'regular'

        return labels

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Assign segments to customers."""
        if self.model is None or self.feature_columns is None:
            raise ValueError("Model not trained. Call train() first.")

        # Prepare features
        df = self.prepare_features(df)

        # Select features
        X = df[self.feature_columns]

        # Scale and predict
        X_scaled = self.scaler.transform(X)
        cluster_labels = self.model.predict(X_scaled)

        # Add cluster and segment to dataframe
        df['cluster'] = cluster_labels
        df['segment'] = df['cluster'].map(self.cluster_labels)

        return df

    def save_model(self, path: str):
        """Save the trained model and scaler."""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'cluster_labels': self.cluster_labels
        }
        joblib.dump(model_data, path)

    def load_model(self, path: str):
        """Load a trained model and scaler."""
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.cluster_labels = model_data['cluster_labels']
