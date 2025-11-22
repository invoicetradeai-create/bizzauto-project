'use client';

import { useState, useEffect } from "react";
import { useTheme } from "@/hooks/use-theme";
import { Button } from "@/components/ui/button";
import { Moon, Sun, Search, Pencil, Trash2, Bell, Menu, Plus, X } from "lucide-react";
import Sidebar, { NavigationContent } from "@/components/Sidebar";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { apiClient } from "@/lib/api-client";
import { API_ENDPOINTS } from "@/lib/api-config";


type Client = {
  id?: string;
  name: string;
  company_id: string;
  phone: string;
  email: string;
  address: string;
};

type Company = {
  id: string;
  name: string;
};

export default function CRMPage() {
  const { theme, toggleTheme } = useTheme();
  const [search, setSearch] = useState("");
  const [open, setOpen] = useState(false);

  const [clients, setClients] = useState<Client[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [showForm, setShowForm] = useState(false);
  const [editingClient, setEditingClient] = useState<Client | null>(null);

  const [formData, setFormData] = useState<Omit<Client, 'id' | 'company_id'>>({
    name: "",
    phone: "",
    email: "",
    address: "",
  });

  const fetchClients = async () => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.clients);
      setClients(Array.isArray(response.data) ? response.data : []);
      setError(null); // Clear any previous errors
    } catch (err: any) {
      // Axios errors are typically in err.response.data or err.message
      setError(err.response?.data?.detail || err.message || "Failed to fetch clients.");
      console.error("Error fetching clients:", err);
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
      await Promise.all([fetchClients(), fetchCompanies()]);
      setLoading(false);
    };
    fetchData();
  }, []);

  const resetForm = () => {
    setFormData({ name: "", phone: "", email: "", address: "" });
    setEditingClient(null);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const companyId = companies[0]?.id;
    if (!companyId) {
      alert("No companies found. Please create a company first.");
      return;
    }
    const newClient = { ...formData, company_id: companyId };
    try {
      const response = await apiClient.post(API_ENDPOINTS.clients, newClient);
      alert("✅ Client created successfully!");
      setShowForm(false);
      fetchClients();
    } catch (err: any) {
      alert(`Create failed: ${err.response?.data?.detail || err.message}`);
      console.error("Error creating client:", err);
    }
  };

  const handleEdit = (client: Client) => {
    setEditingClient(client);
    setFormData({
      name: client.name || "",
      phone: client.phone || "",
      email: client.email || "",
      address: client.address || "",
    });
    setShowForm(true);
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingClient?.id) return;

    const companyId = companies[0]?.id;
    if (!companyId) {
      alert("No companies found. Please create a company first.");
      return;
    }
    
    const payload = { ...formData, company_id: companyId };

    try {
      const response = await apiClient.put(`${API_ENDPOINTS.clients}/${editingClient.id}`, payload);
      alert("✅ Client updated successfully!");
      setShowForm(false);
      fetchClients();
    } catch (err: any) {
      alert(`Update failed: ${err.response?.data?.detail || err.message}`);
      console.error("Error updating client:", err);
    }
  };

  const handleDelete = async (id?: string) => {
    if (!id) return;
    if (!confirm("Are you sure you want to delete this client?")) return;
    try {
      const response = await apiClient.delete(`${API_ENDPOINTS.clients}/${id}`);
      fetchClients();
    } catch (err: any) {
      alert(`Delete failed: ${err.response?.data?.detail || err.message}`);
      console.error("Error deleting client:", err);
    }
  };

  const filtered = clients.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.email.toLowerCase().includes(search.toLowerCase()) ||
      c.phone.includes(search)
  );

  if (loading)
    return (
      <div className="flex justify-center items-center min-h-screen text-gray-600">
        Loading clients...
      </div>
    );

  if (error)
    return (
      <div className="text-red-600 text-center mt-10">
        ❌ Error loading clients: {error}
      </div>
    );

  return (
    <div className="flex min-h-screen bg-background overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-y-auto transition-all duration-300 lg:ml-64">
        <header className="border-b bg-card px-4 py-3 flex items-center justify-between sticky top-0 z-40">
          <div className="flex items-center gap-3 flex-1">
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

            <div className="relative flex-1 max-w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search clients..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 w-full bg-background border border-gray-200 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all duration-300"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="relative hover:bg-blue-50 dark:hover:bg-gray-800 transition">
              <Bell className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 h-4 w-4 bg-destructive rounded-full text-[10px] text-white flex items-center justify-center">
                3
              </span>
            </Button>

            <Button variant="ghost" size="icon" onClick={toggleTheme}>
              {theme === "dark" ? <Sun className="h-5 w-5 text-yellow-400" /> : <Moon className="h-5 w-5 text-blue-500" />}
            </Button>

            <Avatar className="cursor-pointer hover:scale-105 transition-transform duration-200">
              <AvatarFallback className="bg-primary text-primary-foreground">{typeof window !== 'undefined' ? localStorage.getItem("user_avatar")?.charAt(0).toUpperCase() || 'M' : 'M'}</AvatarFallback>
            </Avatar>
          </div>
        </header>

        <div className="p-4 md:p-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <h1 className="text-xl md:text-2xl font-bold">CRM</h1>
            <p className="text-muted-foreground text-sm md:text-base">
              Manage your clients and relationships
            </p>
          </div>

          <button
            onClick={() => {
              resetForm();
              setShowForm(true);
            }}
            className="bg-blue-600 hover:bg-blue-700 text-white text-sm px-4 py-2 rounded-lg flex items-center gap-2 w-full sm:w-auto justify-center"
          >
            <Plus className="w-4 h-4" /> Add Client
          </button>
        </div>

        <div className="px-4 md:px-6 pb-6 overflow-x-auto">
          <div className="w-full bg-card rounded-lg border-border border text-sm overflow-x-auto">
            <table className="w-full min-w-[800px]">
              <thead className="bg-muted text-muted-foreground">
                <tr>
                  <th className="p-3 text-left">Name</th>
                  <th className="p-3 text-left">Email</th>
                  <th className="p-3 text-left">Phone</th>
                  <th className="p-3 text-left">Address</th>
                  <th className="p-3 text-right">Actions</th>
                </tr>
              </thead>

              <tbody>
                {filtered.map((c) => (
                  <tr key={c.id} className="border-b border-border hover:bg-muted text-foreground transition">
                    <td className="p-3">{c.name}</td>
                    <td className="p-3">{c.email}</td>
                    <td className="p-3">{c.phone}</td>
                    <td className="p-3">{c.address}</td>
                    <td className="p-3 flex justify-end gap-3">
                      <Pencil onClick={() => handleEdit(c)} className="w-4 h-4 cursor-pointer hover:text-yellow-600" />
                      <Trash2 onClick={() => handleDelete(c.id)} className="w-4 h-4 cursor-pointer hover:text-red-600" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filtered.length === 0 && (
            <p className="text-center text-muted-foreground text-sm mt-6">
              No clients found.
            </p>
          )}
        </div>

        {showForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-lg shadow-lg">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">
                  {editingClient ? "Edit Client" : "Add Client"}
                </h2>
                <X className="cursor-pointer" onClick={() => setShowForm(false)} />
              </div>

              <form onSubmit={editingClient ? handleUpdate : handleCreate} className="space-y-3">
                <Input
                  placeholder="Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
                <Input
                  placeholder="Email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
                <Input
                  placeholder="Phone"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
                <Input
                  placeholder="Address"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                />

                <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white">
                  {editingClient ? "Update Client" : "Create Client"}
                </Button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}