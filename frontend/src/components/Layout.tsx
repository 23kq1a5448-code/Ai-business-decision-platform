import { Outlet, Link, useLocation } from 'react-router-dom';
import { Layout as LayoutIcon, DollarSign, Users, Package, BarChart3, Brain, LogOut, MessageSquare } from 'lucide-react';
import ChatWidget from './ChatWidget';
import { authService } from '../services/auth';

interface LayoutProps {
  onLogout: () => void;
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutIcon },
  { name: 'Sales', href: '/sales', icon: DollarSign },
  { name: 'Customers', href: '/customers', icon: Users },
  { name: 'Products', href: '/products', icon: Package },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'ML Models', href: '/ml-models', icon: Brain },
];

export default function Layout({ onLogout }: LayoutProps) {
  const location = useLocation();

  const handleLogout = () => {
    onLogout();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-navy-900 text-white">
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-center h-16 border-b border-navy-800">
            <h1 className="text-xl font-bold">AI Business Platform</h1>
          </div>

          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-navy-700 text-white'
                      : 'text-navy-100 hover:bg-navy-800'
                  }`}
                >
                  <item.icon className="w-5 h-5 mr-3" />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          <div className="p-4 border-t border-navy-800">
            <button
              onClick={handleLogout}
              className="flex items-center w-full px-4 py-3 text-navy-100 hover:bg-navy-800 rounded-lg transition-colors"
            >
              <LogOut className="w-5 h-5 mr-3" />
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="ml-64">
        <header className="bg-white border-b border-gray-200 px-8 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold text-gray-900">
              {navigation.find((item) => item.href === location.pathname)?.name || 'Dashboard'}
            </h2>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                {authService.getUser()?.full_name || 'User'}
              </span>
            </div>
          </div>
        </header>

        <main className="p-8">
          <Outlet />
        </main>
      </div>

      {/* Chat Widget - Available on every page */}
      <ChatWidget />
    </div>
  );
}
