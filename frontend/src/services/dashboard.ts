import api from './api';

export interface DashboardMetrics {
  total_revenue: number;
  total_profit: number;
  total_orders: number;
  total_customers: number;
  sales_growth: number | null;
  profit_margin: number;
  previous_period_revenue: number | null;
  previous_period_profit: number | null;
}

export interface DashboardAnalytics {
  revenue_trends: Array<{ date: string; revenue: number }>;
  sales_by_category: Array<{ category: string; total: number }>;
  top_selling_products: Array<{
    name: string;
    total_quantity: number;
    total_revenue: number;
  }>;
  recent_transactions: Array<{
    id: number;
    invoice_number: string;
    sale_date: string;
    total_amount: number;
    status: string;
  }>;
  inventory_warnings: Array<{
    id: number;
    name: string;
    sku: string | null;
    stock_quantity: number;
    low_stock_threshold: number;
  }>;
  ai_insights: string[];
}

export const dashboardService = {
  async getMetrics(startDate?: string, endDate?: string): Promise<DashboardMetrics> {
    const params: Record<string, string> = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response = await api.get<DashboardMetrics>('/dashboard/metrics', { params });
    return response.data;
  },

  async getAnalytics(startDate?: string, endDate?: string): Promise<DashboardAnalytics> {
    const params: Record<string, string> = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response = await api.get<DashboardAnalytics>('/dashboard/analytics', { params });
    return response.data;
  },
};
