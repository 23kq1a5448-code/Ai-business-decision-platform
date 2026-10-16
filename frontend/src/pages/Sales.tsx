import { useState, useEffect } from 'react';
import { format, subDays } from 'date-fns';
import { Plus, Download, Search, Filter } from 'lucide-react';
import api from '../services/api';

interface Sale {
  id: number;
  invoice_number: string;
  sale_date: string;
  total_amount: number;
  total_profit: number;
  status: string;
  customer_id: number | null;
}

export default function Sales() {
  const [sales, setSales] = useState<Sale[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadSales();
  }, []);

  const loadSales = async () => {
    try {
      const response = await api.get<Sale[]>('/sales/');
      setSales(response.data);
    } catch (error) {
      console.error('Failed to load sales:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredSales = sales.filter(
    (sale) =>
      sale.invoice_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      sale.status.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search sales..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 input w-64"
            />
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button className="btn-secondary flex items-center">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
          <button className="btn-primary flex items-center">
            <Plus className="w-4 h-4 mr-2" />
            New Sale
          </button>
        </div>
      </div>

      {/* Sales Table */}
      <div className="card overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-navy-600"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Invoice #</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Date</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Amount</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Profit</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredSales.map((sale) => (
                  <tr key={sale.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium text-navy-600">{sale.invoice_number}</td>
                    <td className="py-3 px-4 text-gray-600">
                      {format(new Date(sale.sale_date), 'MMM dd, yyyy')}
                    </td>
                    <td className="py-3 px-4 font-semibold text-gray-900">
                      ${sale.total_amount.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-gray-600">
                      ${sale.total_profit.toLocaleString()}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          sale.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : sale.status === 'pending'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {sale.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {filteredSales.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-600">No sales found</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
