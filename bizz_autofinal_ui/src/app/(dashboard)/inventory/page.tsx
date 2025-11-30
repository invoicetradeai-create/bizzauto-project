"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { useTheme } from "@/hooks/use-theme";
import { Button } from "@/components/ui/button";
import { Moon, Sun, Bell, Menu, Search, Plus, Edit3, Trash2, AlertTriangle, X } from "lucide-react";
import Sidebar, { NavigationContent } from "@/components/Sidebar";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { apiClient } from "@/lib/api-client";
import { API_ENDPOINTS } from "@/lib/api-config";
import OcrUploadCard from "@/components/OcrUploadCard";


type Product = {
  id?: string;
  name: string;
  sku: string;
  category: string;
  purchase_price: number;
  sale_price: number;
  stock_quantity: number;
  unit: string;
  low_stock_alert?: number;
  expiration_date?: string | null;
};

type Company = {
  id: string;
  name: string;
};

export default function InventoryPage() {
  const router = useRouter();
  const { theme, toggleTheme, mounted } = useTheme();
  const [search, setSearch] = useState("");

  const [open, setOpen] = useState(false);

  const [products, setProducts] = useState<Product[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [showForm, setShowForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [showOcrUpload, setShowOcrUpload] = useState(false);

  const [formData, setFormData] = useState<Product>({
    name: "",
    sku: "",
    category: "",
    purchase_price: 0,
    sale_price: 0,
    stock_quantity: 0,
    unit: "pcs",
    low_stock_alert: 5,
    expiration_date: "",
  });

  // ✅ Fetch Products
  const fetchProducts = async () => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.products);
      setProducts(Array.isArray(response.data) ? response.data : []);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || "Failed to fetch products.");
      console.error("Error fetching products:", err);
    }
  };

  const fetchCompanies = async () => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.companies);
      if (response.data && Array.isArray(response.data)) {
        setCompanies(response.data);
      }
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || "Failed to fetch companies.");
      console.error("Error fetching companies:", err);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      await Promise.all([fetchProducts(), fetchCompanies()]);
      setLoading(false);
    };
    fetchData();
  }, []);

  // ✅ Handlers
  const resetForm = () => {
    setFormData({
      name: "",
      sku: "",
      category: "",
      purchase_price: 0,
      sale_price: 0,
      stock_quantity: 0,
      unit: "pcs",
      low_stock_alert: 5,
      expiration_date: "",
    });
    setEditingProduct(null);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const companyId = companies[0]?.id;
    if (!companyId) {
      alert("No companies found. Please create a company first.");
      return;
    }
    const newProduct = { ...formData, company_id: companyId };
    try {
      const response = await apiClient.post(API_ENDPOINTS.products, newProduct);
      alert("✅ Product created successfully!");
      setShowForm(false);
      fetchProducts();
    } catch (err: any) {
      alert(`Create failed: ${err.response?.data?.detail || err.message}`);
      console.error("Error creating product:", err);
    }
  };

  const handleEdit = (product: Product) => {
    setEditingProduct(product);
    setFormData({
      ...product,
      name: product.name || "",
      sku: product.sku || "",
      category: product.category || "",
      unit: product.unit || "",
      purchase_price: product.purchase_price || 0,
      sale_price: product.sale_price || 0,
      stock_quantity: product.stock_quantity || 0,
      low_stock_alert: product.low_stock_alert || 5,
      expiration_date: product.expiration_date ? new Date(product.expiration_date).toISOString().split('T')[0] : "",
    });
    setShowForm(true);
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingProduct?.id) return;
    
    const companyId = companies[0]?.id;
    if (!companyId) {
      alert("No companies found. Please create a company first.");
      return;
    }

    const { id, ...updateData } = formData;
    const payload = { ...updateData, company_id: companyId };

    try {
      const response = await apiClient.put(`${API_ENDPOINTS.products}/${editingProduct.id}`, payload);
      alert("✅ Product updated successfully!");
      setShowForm(false);
      fetchProducts();
    } catch (err: any) {
      alert(`Update failed: ${err.response?.data?.detail || err.message}`);
      console.error("Error updating product:", err);
    }
  };

  const handleDelete = async (id?: string) => {
    if (!id) return;
    if (!confirm("Are you sure you want to delete this product?")) return;
    try {
      const response = await apiClient.delete(`${API_ENDPOINTS.products}/${id}`);
      fetchProducts();
    } catch (err: any) {
      alert(`Delete failed: ${err.response?.data?.detail || err.message}`);
      console.error("Error deleting product:", err);
    }
  };

  const filtered = products.filter(
    (p) =>
      p.name?.toLowerCase().includes(search.toLowerCase()) ||
      p.sku?.toLowerCase().includes(search.toLowerCase()) ||
      p.category?.toLowerCase().includes(search.toLowerCase())
  );

  if (loading)
    return (
      <div className="flex justify-center items-center min-h-screen text-gray-600">
        Loading products...
      </div>
    );

  if (error)
    return (
      <div className="text-red-600 text-center mt-10">
        ❌ Error loading products: {error}
      </div>
    );

  return (
    <div className="flex min-h-screen bg-background overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-y-auto transition-all duration-300 lg:ml-64">
        {/* Header */}
        <header className="border-b bg-card px-4 py-3 flex items-center justify-between sticky top-0 z-40">
          <div className="flex items-center gap-3 flex-1">
            {/* Mobile Sidebar */}
            <Sheet open={open} onOpenChange={setOpen}>
              <SheetTrigger asChild className="lg:hidden">
                <Button variant="outline" size="icon">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="p-0 w-64">
                <SheetHeader className="px-4 py-2 border-b dark:border-gray-800">
                  <SheetTitle>Dashboard Navigation</SheetTitle>
                </SheetHeader>
                <NavigationContent setOpen={setOpen} />
              </SheetContent>
            </Sheet>

            {/* Search Bar */}
            <div className="relative flex-1 max-w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search products..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 w-full bg-background border border-gray-200 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all duration-300"
              />
            </div>
          </div>

          {/* Right Icons */}
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="relative hover:bg-blue-50 dark:hover:bg-gray-800 transition">
              <Bell className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 h-4 w-4 bg-destructive rounded-full text-[10px] text-white flex items-center justify-center">
                3
              </span>
            </Button>

            <Button variant="ghost" size="icon" onClick={toggleTheme}>
              {mounted && theme === "dark" ? <Sun className="h-5 w-5 text-yellow-400" /> : <Moon className="h-5 w-5 text-blue-500" />}
            </Button>

            <div onClick={() => router.push('/settings')} className="cursor-pointer hover:scale-105 transition-transform duration-200">
              <Avatar>
                <AvatarFallback className="bg-primary text-primary-foreground">{mounted ? localStorage.getItem("user_avatar")?.charAt(0).toUpperCase() || 'M' : 'M'}</AvatarFallback>
              </Avatar>
            </div>
          </div>
        </header>

        {/* Page Header */}
        <div className="p-4 md:p-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <h1 className="text-xl md:text-2xl font-bold">Inventory</h1>
            <p className="text-muted-foreground text-sm md:text-base">Track and manage your product inventory</p>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => {
                resetForm();
                setShowForm(true);
              }}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm"
            >
              <Plus className="w-4 h-4" /> Add New Product
            </button>
            <button
              onClick={() => setShowOcrUpload(true)}
              className="bg-white hover:bg-gray-100 text-black border border-black px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-bold cursor-pointer transition duration-200 ease-in-out hover:shadow-md"
            >
              PDF Upload
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="px-4 md:px-6 overflow-auto mb-8">
          <div className="w-full bg-card rounded-lg border-border border text-sm overflow-x-auto">
            <table className="w-full min-w-[800px]">
              <thead className="bg-muted text-muted-foreground">
                <tr>
                  <th className="p-3 text-left">Name</th>
                  <th className="p-3 text-left">SKU</th>
                  <th className="p-3 text-left">Category</th>
                  <th className="p-3 text-left">Stock</th>
                  <th className="p-3 text-left">Price</th>
                  <th className="p-3 text-left">Status</th>
                  <th className="p-3 text-right">Actions</th>
                </tr>
              </thead>

              <tbody>
  {filtered.map((p, index) => {
    const isLowStock = p.stock_quantity < 20;
    return (
      <tr
        key={p.id || `${p.sku}-${index}`} // ✅ fallback if id is missing
        className={`border-b border-border ${
          isLowStock ? "bg-destructive/10" : "hover:bg-muted"
        }`}
      >
        <td className="p-3">{p.name}</td>
        <td className="p-3">{p.sku}</td>
        <td className="p-3">{p.category}</td>
        <td className="p-3">{p.stock_quantity}</td>
        <td className="p-3">Rs {p.sale_price}</td>
        <td className="p-3">
          {isLowStock ? (
            <span className="bg-red-100 text-red-700 px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1 w-fit">
              <AlertTriangle className="w-3 h-3" /> Low Stock
            </span>
          ) : (
            <span className="bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-medium">
              In Stock
            </span>
          )}
        </td>
        <td className="p-3 flex justify-end gap-3">
          <Edit3
            onClick={() => handleEdit(p)}
            className="w-4 h-4 cursor-pointer text-muted-foreground hover:text-primary"
          />
          <Trash2
            onClick={() => handleDelete(p.id)}
            className="w-4 h-4 cursor-pointer text-muted-foreground hover:text-destructive"
          />
        </td>
      </tr>
    );
  })}
</tbody>

            </table>
          </div>
        </div>

        {/* Form Modal */}
        {showForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-2xl shadow-lg max-h-full overflow-y-auto">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">
                  {editingProduct ? "Edit Product" : "Add Product"}
                </h2>
                <X className="cursor-pointer" onClick={() => setShowForm(false)} />
              </div>

              <form onSubmit={editingProduct ? handleUpdate : handleCreate} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Name</label>
                    <Input id="name" placeholder="Product ka naam" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} required />
                  </div>
                  <div>
                    <label htmlFor="sku" className="block text-sm font-medium text-gray-700 dark:text-gray-300">SKU</label>
                    <Input id="sku" placeholder="Product ka unique code" value={formData.sku} onChange={(e) => setFormData({ ...formData, sku: e.target.value })} required />
                  </div>
                  <div>
                    <label htmlFor="category" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Category</label>
                    <Input id="category" placeholder="Product ki category" value={formData.category} onChange={(e) => setFormData({ ...formData, category: e.target.value })} />
                  </div>
                  <div>
                    <label htmlFor="purchase_price" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Purchase Price</label>
                    <Input id="purchase_price" type="number" placeholder="Product ka kharid price" value={formData.purchase_price} onChange={(e) => setFormData({ ...formData, purchase_price: Number(e.target.value) })} />
                  </div>
                  <div>
                    <label htmlFor="sale_price" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Sale Price</label>
                    <Input id="sale_price" type="number" placeholder="Product ka bechne ka price" value={formData.sale_price} onChange={(e) => setFormData({ ...formData, sale_price: Number(e.target.value) })} />
                  </div>
                  <div>
                    <label htmlFor="stock_quantity" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Stock Quantity</label>
                    <Input id="stock_quantity" type="number" placeholder="Product ki available quantity" value={formData.stock_quantity} onChange={(e) => setFormData({ ...formData, stock_quantity: Number(e.target.value) })} />
                  </div>
                  <div>
                    <label htmlFor="unit" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Unit</label>
                    <Input id="unit" placeholder="e.g., pcs, kg (Measurement unit jaise pcs, kg)" value={formData.unit} onChange={(e) => setFormData({ ...formData, unit: e.target.value })} />
                  </div>
                  <div>
                    <label htmlFor="low_stock_alert" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Low Stock Alert</label>
                    <Input id="low_stock_alert" type="number" placeholder="Jab stock kam ho jaye alert" value={formData.low_stock_alert} onChange={(e) => setFormData({ ...formData, low_stock_alert: Number(e.target.value) })} />
                  </div>
                  <div className="md:col-span-2">
                    <label htmlFor="expiration_date" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Expiration Date</label>
                    <Input id="expiration_date" type="date" placeholder="Product ki expiry date" value={formData.expiration_date || ""} onChange={(e) => setFormData({ ...formData, expiration_date: e.target.value })} />
                  </div>
                </div>

                <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white">
                  {editingProduct ? "Update Product" : "Create Product"}
                </Button>
              </form>
            </div>
          </div>
        )}
        {showOcrUpload && <OcrUploadCard onClose={() => setShowOcrUpload(false)} />}
      </div>
    </div>
  );
}
