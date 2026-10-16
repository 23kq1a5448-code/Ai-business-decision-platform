import { useState, useEffect } from 'react';
import { Plus, Search, AlertTriangle } from 'lucide-react';
import api from '../services/api';

interface Customer {
  id: number;
  name: string;
  email: string | null;
  phone: string | null;
  segment: string | null;
  churn_risk: string | null;
  churn_probability: number | null;
  created_at: string;
}

export default function Customers() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    try {
      const response = await api.get<Customer[]>('/customers/');
      setCustomers(response.data);
    } catch (error) {
      console.error('Failed to load customers:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredCustomers = customers.filter(
    (customer) =>
      customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (customer.email && customer.email.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const getChurnRiskColor = (risk: string | null) => {
    switch (risk) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search customers..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 input w-64"
          />
        </div>
        <button className="btn-primary flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          Add Customer
        </button>
      </div>

      {/* Customers Table */}
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
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Name</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Email</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Phone</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Segment</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Churn Risk</th>
                </tr>
              </thead>
              <tbody>
                {filteredCustomers.map((customer) => (
                  <tr key={customer.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium text-gray-900">{customer.name}</td>
                    <td className="py-3 px-4 text-gray-600">{customer.email || 'N/A'}</td>
                    <td className="py-3 px-4 text-gray-600">{customer.phone || 'N/A'}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-1 rounded-full text-xs font-medium bg-navy-100 text-navy-800">
                        {customer.segment || 'N/A'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      {customer.churn_risk === 'high' && (
                        <div className="flex items-center space-x-2">
                          <AlertTriangle className="w-4 h-4 text-red-600" />
                          <span
                            className={`px-2 py-1 rounded-full text-xs font-medium ${getChurnRiskColor(customer.churn_risk)}`}
                          >
                            {customer.churn_risk}
                          </span>
                        </div>
                      )}
                      {customer.churn_risk !== 'high' && (
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${getChurnRiskColor(customer.churn_risk)}`}
                        >
                          {customer.churn_risk || 'N/A'}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {filteredCustomers.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-600">No customers found</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
