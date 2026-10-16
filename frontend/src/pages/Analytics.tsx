import { useState, useEffect } from 'react';
import { format, subDays } from 'date-fns';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import api from '../services/api';

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6'];

export default function Analytics() {
  const [financialData, setFinancialData] = useState<any>(null);
  const [salesData, setSalesData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const endDate = new Date();
      const startDate = subDays(endDate, 30);

      const [financial, sales] = await Promise.all([
        api.get('/analytics/financial', {
          params: {
            start_date: startDate.toISOString(),
            end_date: endDate.toISOString(),
          },
        }),
        api.get('/analytics/sales', {
          params: {
            start_date: startDate.toISOString(),
            end_date: endDate.toISOString(),
          },
        }),
      ]);

      setFinancialData(financial.data);
      setSalesData(sales.data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
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

  return (
    <div className="space-y-6">
      {/* Financial Summary Cards */}
      {financialData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <SummaryCard title="Total Revenue" value={`$${financialData.total_revenue.toLocaleString()}`} />
          <SummaryCard title="Gross Profit" value={`$${financialData.gross_profit.toLocaleString()}`} />
          <SummaryCard title="Operating Expenses" value={`$${financialData.operating_expenses.toLocaleString()}`} />
          <SummaryCard title="Net Profit" value={`$${financialData.net_profit.toLocaleString()}`} />
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Financial Trends */}
        {financialData && financialData.monthly_trends.length > 0 && (
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Monthly Financial Trends</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={financialData.monthly_trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis tickFormatter={(value) => `$${value.toLocaleString()}`} />
                <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
                <Legend />
                <Bar dataKey="revenue" fill="#6366f1" name="Revenue" />
                <Bar dataKey="cost" fill="#ef4444" name="Cost" />
                <Bar dataKey="profit" fill="#10b981" name="Profit" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Sales by Region */}
        {salesData && salesData.sales_by_region.length > 0 && (
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Sales by Region</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={salesData.sales_by_region}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ region, percent }) => `${region} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="total"
                >
                  {salesData.sales_by_region.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Product Profitability */}
      {financialData && financialData.product_profitability.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Product Profitability</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={financialData.product_profitability.slice(0, 10)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis tickFormatter={(value) => `$${value.toLocaleString()}`} />
              <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
              <Legend />
              <Bar dataKey="profit" fill="#10b981" name="Profit" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Expense Categories */}
      {financialData && financialData.expense_categories.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Expense Categories</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={financialData.expense_categories}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ category, percent }) => `${category} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="total"
              >
                {financialData.expense_categories.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

interface SummaryCardProps {
  title: string;
  value: string;
}

function SummaryCard({ title, value }: SummaryCardProps) {
  return (
    <div className="card">
      <p className="text-sm text-gray-600">{title}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}
