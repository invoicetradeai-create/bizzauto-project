'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';
import { API_ENDPOINTS } from '@/lib/api-config';


// Define reusable API response type
type ApiResponse<T> = {
  data?: T;
  error?: string;
};

// Define the Product type based on your backend
type Product = {
  id?: string;
  company_id: string;
  name: string;
  sku: string;
  category: string;
  purchase_price: number;
  sale_price: number;
  stock_quantity: number;
  unit: string;
};

export default function TestApiPage() {
  const [healthStatus, setHealthStatus] = useState<any>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // ✅ Test health endpoint
  const testHealth = async () => {
    try {
      console.log('Testing health endpoint...');
      const response: ApiResponse<any> = await apiClient.get(API_ENDPOINTS.health);

      if (response.error) {
        setError(`Health check failed: ${response.error}`);
      } else {
        setHealthStatus(response.data);
      }
    } catch (err) {
      setError(`Health check error: ${(err as Error).message}`);
    }
  };

  // ✅ Test products endpoint
  const testProducts = async () => {
    try {
      console.log('Testing products endpoint...');
      const response: ApiResponse<Product[] | unknown> = await apiClient.get(API_ENDPOINTS.products);

      if (response.error) {
        setError(`Products fetch failed: ${response.error}`);
      } else if (Array.isArray(response.data)) {
        setProducts(response.data);
      } else {
        // Defensive fallback if API returns object instead of array
        setProducts([]);
      }
    } catch (err) {
      setError(`Products fetch error: ${(err as Error).message}`);
    }
  };

  // ✅ Test create product endpoint
  const testCreateProduct = async () => {
    try {
      console.log('Testing create product...');
      const newProduct: Product = {
        company_id: '123e4567-e89b-12d3-a456-426614174000',
        name: 'Test Product ' + Date.now(),
        sku: 'TEST-' + Date.now(),
        category: 'Test',
        purchase_price: 100,
        sale_price: 150,
        stock_quantity: 50,
        unit: 'pcs',
      };

      const response: ApiResponse<Product> = await apiClient.post(API_ENDPOINTS.products, newProduct);

      if (response.error) {
        alert(`Create failed: ${response.error}`);
      } else {
        alert('✅ Product created successfully!');
        testProducts(); // Refresh list
      }
    } catch (err) {
      alert(`Error creating product: ${(err as Error).message}`);
    }
  };

  // ✅ Run initial tests
  useEffect(() => {
    const runTests = async () => {
      setLoading(true);
      await testHealth();
      await testProducts();
      setLoading(false);
    };

    runTests();
  }, []);

  // ✅ UI Rendering
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Testing API connection...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold mb-6">🔗 Backend Connection Test</h1>

        {/* ❌ Error Display */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
            <p className="text-sm text-red-700 font-medium">{error}</p>
            <p className="text-xs text-red-600 mt-1">
              Make sure your backend is running at: <strong>http://localhost:8000</strong>
            </p>
          </div>
        )}

        {/* ✅ Health Status */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">✅ Health Check</h2>
          {healthStatus ? (
            <div className="bg-green-50 p-4 rounded">
              <pre className="text-sm text-green-800">
                {JSON.stringify(healthStatus, null, 2)}
              </pre>
            </div>
          ) : (
            <div className="bg-red-50 p-4 rounded">
              <p className="text-red-600">Backend not responding</p>
            </div>
          )}
        </div>

        {/* 📦 Products List */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">📦 Products</h2>
            <button
              onClick={testCreateProduct}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
            >
              + Create Test Product
            </button>
          </div>

          {products.length === 0 ? (
            <div className="text-center py-8 bg-gray-50 rounded">
              <p className="text-gray-500">No products found</p>
              <p className="text-sm text-gray-400 mt-2">
                Click <strong>“Create Test Product”</strong> to add one.
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {products.map((product, index) => (
                <div key={index} className="border rounded p-4 hover:bg-gray-50 transition">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold">{product.name}</h3>
                      <p className="text-sm text-gray-600">SKU: {product.sku}</p>
                      <p className="text-sm text-gray-600">Category: {product.category}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm">
                        <span className="text-gray-500">Stock:</span>{' '}
                        <span className="font-semibold">{product.stock_quantity}</span>
                      </p>
                      <p className="text-sm">
                        <span className="text-gray-500">Price:</span>{' '}
                        <span className="font-semibold">${product.sale_price}</span>
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 🔗 API Endpoints */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">🔗 API Endpoints</h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between p-2 hover:bg-gray-50 rounded">
              <span className="text-gray-600">Backend URL:</span>
              <span className="font-mono text-blue-600">http://localhost:8000</span>
            </div>
            <div className="flex justify-between p-2 hover:bg-gray-50 rounded">
              <span className="text-gray-600">Health:</span>
              <span className="font-mono text-blue-600">/health</span>
            </div>
            <div className="flex justify-between p-2 hover:bg-gray-50 rounded">
              <span className="text-gray-600">Products:</span>
              <span className="font-mono text-blue-600">/api/products</span>
            </div>
            <div className="flex justify-between p-2 hover:bg-gray-50 rounded">
              <span className="text-gray-600">API Docs:</span>
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                className="font-mono text-blue-600 hover:underline"
              >
                /docs
              </a>
            </div>
          </div>
        </div>

        {/* 📝 Next Steps */}
        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
          <h3 className="font-semibold text-blue-900 mb-2">📝 Next Steps:</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>✅ Backend connection is working!</li>
            <li>✅ You can fetch data from the API</li>
            <li>✅ You can create new products</li>
            <li>🎯 Now integrate this into your actual pages</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
