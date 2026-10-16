import { useState, useEffect } from 'react';
import { Play, TrendingUp, Users, Package, AlertTriangle, GitBranch } from 'lucide-react';
import api from '../services/api';

interface ModelRun {
  id: number;
  model_type: string;
  model_name: string;
  algorithm: string;
  status: string;
  metrics: Record<string, any>;
  created_at: string;
}

export default function MLModels() {
  const [models, setModels] = useState<ModelRun[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const response = await api.get<ModelRun[]>('/ml/models/');
      setModels(response.data);
    } catch (error) {
      console.error('Failed to load models:', error);
    } finally {
      setLoading(false);
    }
  };

  const trainModel = async (modelType: string) => {
    try {
      await api.post(`/ml/${modelType}/train`, {
        model_name: `${modelType}_model`,
        algorithm: 'RandomForest',
      });
      loadModels();
    } catch (error) {
      console.error('Failed to train model:', error);
      alert('Failed to train model');
    }
  };

  const getModelIcon = (modelType: string) => {
    switch (modelType) {
      case 'sales_prediction':
        return <TrendingUp className="w-5 h-5" />;
      case 'churn_prediction':
        return <Users className="w-5 h-5" />;
      case 'demand_forecast':
        return <Package className="w-5 h-5" />;
      case 'anomaly_detection':
        return <AlertTriangle className="w-5 h-5" />;
      case 'segmentation':
        return <GitBranch className="w-5 h-5" />;
      default:
        return <TrendingUp className="w-5 h-5" />;
    }
  };

  const getModelDisplayName = (modelType: string) => {
    switch (modelType) {
      case 'sales_prediction':
        return 'Sales Prediction';
      case 'churn_prediction':
        return 'Customer Churn Prediction';
      case 'demand_forecast':
        return 'Demand Forecasting';
      case 'anomaly_detection':
        return 'Anomaly Detection';
      case 'segmentation':
        return 'Customer Segmentation';
      default:
        return modelType;
    }
  };

  const modelTypes = [
    'sales_prediction',
    'churn_prediction',
    'demand_forecast',
    'segmentation',
    'anomaly_detection',
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Machine Learning Models</h2>
        <p className="text-gray-600">Train and manage your ML models for business intelligence</p>
      </div>

      {/* Model Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {modelTypes.map((modelType) => {
          const latestModel = models
            .filter((m) => m.model_type === modelType)
            .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0];

          return (
            <div key={modelType} className="card">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-3 bg-navy-100 rounded-lg text-navy-600">
                    {getModelIcon(modelType)}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{getModelDisplayName(modelType)}</h3>
                    <p className="text-sm text-gray-600">
                      {latestModel ? latestModel.algorithm : 'Not trained yet'}
                    </p>
                  </div>
                </div>
              </div>

              {latestModel ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Status:</span>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        latestModel.status === 'completed'
                          ? 'bg-green-100 text-green-800'
                          : latestModel.status === 'training'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {latestModel.status}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Last trained:</span>
                    <span className="text-gray-900">
                      {new Date(latestModel.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {latestModel.metrics && Object.keys(latestModel.metrics).length > 0 && (
                    <div className="pt-2 border-t border-gray-200">
                      <p className="text-sm font-medium text-gray-900 mb-2">Metrics:</p>
                      <div className="space-y-1">
                        {Object.entries(latestModel.metrics).map(([key, value]) => (
                          <div key={key} className="flex justify-between text-sm">
                            <span className="text-gray-600">{key}:</span>
                            <span className="text-gray-900 font-medium">
                              {typeof value === 'number' ? value.toFixed(4) : value}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-sm text-gray-600 text-center py-4">No model trained yet</p>
              )}

              <button
                onClick={() => trainModel(modelType)}
                className="w-full mt-4 btn-primary flex items-center justify-center"
              >
                <Play className="w-4 h-4 mr-2" />
                Train Model
              </button>
            </div>
          );
        })}
      </div>

      {/* All Models Table */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Training History</h3>
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-navy-600"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Model</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Algorithm</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Status</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Created</th>
                </tr>
              </thead>
              <tbody>
                {models.map((model) => (
                  <tr key={model.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium text-gray-900">{getModelDisplayName(model.model_type)}</td>
                    <td className="py-3 px-4 text-gray-600">{model.algorithm}</td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          model.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : model.status === 'training'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {model.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-600">
                      {new Date(model.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {models.length === 0 && (
              <div className="text-center py-8">
                <p className="text-gray-600">No models trained yet</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
