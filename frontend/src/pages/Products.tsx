import { useState, useEffect } from 'react';
import { Plus, Search, AlertTriangle } from 'lucide-react';
import api from '../services/api';

interface Product {
  id: number;
  name: string;
  sku: string | null;
  selling_price: number;
  cost_price: number;
  stock_quantity: number;
  low_stock_threshold: number;
  predicted_demand: number | null;
  suggested_reorder: number | null;
}

export default function Products() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showLowStockOnly, setShowLowStockOnly] = useState(false);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const response = await api.get<Product[]>('/products/');
      setProducts(response.data);
    } catch (error) {
      console.error('Failed to load products:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredProducts = products.filter(
    (product) =>
      (product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (product.sku && product.sku.toLowerCase().includes(searchTerm.toLowerCase()))) &&
      (!showLowStockOnly || product.stock_quantity <= product.low_stock_threshold)
  );

  const getProfitMargin = (product: Product) => {
    return ((product.selling_price - product.cost_price) / product.selling_price) * 100;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 input w-64"
            />
          </div>
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showLowStockOnly}
              onChange={(e) => setShowLowStockOnly(e.target.checked)}
              className="rounded border-gray-300 text-navy-600 focus:ring-navy-500"
            />
            <span className="text-sm text-gray-600">Low Stock Only</span>
          </label>
        </div>
        <button className="btn-primary flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          Add Product
        </button>
      </div>

      {/* Products Table */}
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
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">SKU</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Selling Price</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Cost</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Stock</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Margin</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredProducts.map((product) => (
                  <tr key={product.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium text-gray-900">{product.name}</td>
                    <td className="py-3 px-4 text-gray-600">{product.sku || 'N/A'}</td>
                    <td className="py-3 px-4 text-gray-900">${product.selling_price.toFixed(2)}</td>
                    <td className="py-3 px-4 text-gray-600">${product.cost_price.toFixed(2)}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-gray-900">{product.stock_quantity}</span>
                        {product.stock_quantity <= product.low_stock_threshold && (
                          <AlertTriangle className="w-4 h-4 text-yellow-600" />
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-gray-600">{getProfitMargin(product).toFixed(1)}%</td>
                    <td className="py-3 px-4">
                      {product.stock_quantity <= product.low_stock_threshold ? (
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          Low Stock
                        </span>
                      ) : (
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          In Stock
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {filteredProducts.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-600">No products found</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
