import { useState, useEffect } from 'react';
import { format, subDays } from 'date-fns';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  ShoppingCart,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { dashboardService, DashboardMetrics, DashboardAnalytics } from '../services/dashboard';

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];

export default function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const endDate = new Date();
      const startDate = subDays(endDate, 30);

      const [metricsData, analyticsData] = await Promise.all([
        dashboardService.getMetrics(startDate.toISOString(), endDate.toISOString()),
        dashboardService.getAnalytics(startDate.toISOString(), endDate.toISOString()),
      ]);

      setMetrics(metricsData);
      setAnalytics(analyticsData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-navy-600"></div>
      </div>
    );
  }

  if (!metrics || !analytics) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Failed to load dashboard data</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Revenue"
          value={`$${metrics.total_revenue.toLocaleString()}`}
          change={metrics.sales_growth}
          icon={<DollarSign className="w-5 h-5" />}
        />
        <MetricCard
          title="Total Profit"
          value={`$${metrics.total_profit.toLocaleString()}`}
          change={metrics.sales_growth}
          icon={<TrendingUp className="w-5 h-5" />}
        />
        <MetricCard
          title="Total Orders"
          value={metrics.total_orders.toString()}
          icon={<ShoppingCart className="w-5 h-5" />}
        />
        <MetricCard
          title="Total Customers"
          value={metrics.total_customers.toString()}
          icon={<Users className="w-5 h-5" />}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Trends */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Revenue Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={analytics.revenue_trends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tickFormatter={(value) => format(new Date(value), 'MMM dd')} />
              <YAxis tickFormatter={(value) => `$${value.toLocaleString()}`} />
              <Tooltip
                labelFormatter={(value) => format(new Date(value), 'MMM dd, yyyy')}
                formatter={(value: number) => [`$${value.toLocaleString()}`, 'Revenue']}
              />
              <Line type="monotone" dataKey="revenue" stroke="#6366f1" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Sales by Category */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Sales by Category</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={analytics.sales_by_category}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="total"
              >
                {analytics.sales_by_category.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Products & Recent Transactions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Selling Products */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Top Selling Products</h3>
          <div className="space-y-3">
            {analytics.top_selling_products.slice(0, 5).map((product, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{product.name}</p>
                  <p className="text-sm text-gray-600">{product.total_quantity} units sold</p>
                </div>
                <p className="font-semibold text-navy-600">
                  ${product.total_revenue.toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Recent Transactions</h3>
          <div className="space-y-3">
            {analytics.recent_transactions.slice(0, 5).map((transaction) => (
              <div key={transaction.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{transaction.invoice_number}</p>
                  <p className="text-sm text-gray-600">{format(new Date(transaction.sale_date), 'MMM dd, yyyy')}</p>
                </div>
                <p className="font-semibold text-navy-600">
                  ${transaction.total_amount.toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Inventory Warnings & AI Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Inventory Warnings */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2 text-yellow-600" />
            Inventory Warnings
          </h3>
          {analytics.inventory_warnings.length > 0 ? (
            <div className="space-y-3">
              {analytics.inventory_warnings.slice(0, 5).map((warning) => (
                <div key={warning.id} className="flex items-center justify-between p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{warning.name}</p>
                    <p className="text-sm text-gray-600">SKU: {warning.sku || 'N/A'}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-yellow-700">{warning.stock_quantity} left</p>
                    <p className="text-sm text-gray-600">Threshold: {warning.low_stock_threshold}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-600 text-center py-4">No inventory warnings</p>
          )}
        </div>

        {/* AI Insights */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">AI Insights</h3>
          <div className="space-y-3">
            {analytics.ai_insights.map((insight, index) => (
              <div key={index} className="p-3 bg-navy-50 border border-navy-200 rounded-lg">
                <p className="text-sm text-navy-900">{insight}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: string;
  change?: number | null;
  icon: React.ReactNode;
}

function MetricCard({ title, value, change, icon }: MetricCardProps) {
  const isPositive = change !== null && change >= 0;

  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div className="p-3 bg-navy-100 rounded-lg text-navy-600">{icon}</div>
        {change !== null && (
          <div className={`flex items-center ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
            {isPositive ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
            <span className="text-sm font-medium ml-1">{Math.abs(change).toFixed(1)}%</span>
          </div>
        )}
      </div>
      <div className="mt-4">
        <p className="text-sm text-gray-600">{title}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
      </div>
    </div>
  );
}
