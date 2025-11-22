"use client";

import { useState, useEffect, useCallback } from "react";
import { useTheme } from "@/hooks/use-theme";
import { Button } from "@/components/ui/button";
import { Moon, Sun, Bell, Menu, Search, Upload, Plus, MoreHorizontal, Trash2, Edit } from "lucide-react";
import Sidebar, { NavigationContent } from "@/components/Sidebar";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle } from "@/components/ui/sheet";

import InvoiceForm from "@/components/InvoiceForm";
import { UUID } from "crypto";
import { apiClient } from "@/lib/api-client";

// Based on the backend Pydantic model
type Invoice = {
  id: UUID;
  company_id: UUID;
  client_id?: UUID;
  invoice_date: string;
  total_amount: number;
  payment_status?: string;
  notes?: string;
};

export default function InvoicesPage() {
  const { theme, toggleTheme } = useTheme();
  const [search, setSearch] = useState("");
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  const [editingInvoice, setEditingInvoice] = useState<Invoice | null>(null);

  const fetchInvoices = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<Invoice[]>('/api/invoices');
      if (response.data) {
        setInvoices(response.data);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || "Failed to fetch invoices");
      console.error("Error fetching invoices:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInvoices();
  }, [fetchInvoices]);

  const handleFormSubmit = async (invoiceData: Omit<Invoice, 'id' | 'company_id'>) => {
    try {
      if (editingInvoice) {
        // Update logic
        const response = await apiClient.put<Invoice>(`/api/invoices/${editingInvoice.id}`, invoiceData);
        if (response.data) {
          await fetchInvoices();
          setIsSheetOpen(false);
          setEditingInvoice(null);
        }
      } else {
        // Create logic
        const companyId = invoices.length > 0 ? invoices[0].company_id : "00000000-0000-0000-0000-000000000000";
        if (companyId === "00000000-0000-0000-0000-000000000000" && invoices.length === 0) {
          setError("Cannot create invoice: No company context available.");
          setIsSheetOpen(false);
          return;
        }
        const newInvoice = { ...invoiceData, company_id: companyId as UUID };
        const response = await apiClient.post<Invoice>('/api/invoices', newInvoice);
        if (response.data) {
          await fetchInvoices();
          setIsSheetOpen(false);
        }
      }
      setError(null); // Clear any previous errors on successful submit
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || (editingInvoice ? "Failed to update invoice." : "Failed to create invoice."));
      console.error("Error submitting invoice:", err);
    }
  };

  const handleDeleteInvoice = async (invoiceId: UUID) => {
    if (window.confirm("Are you sure you want to delete this invoice?")) {
      try {
        const response = await apiClient.delete(`/api/invoices/${invoiceId}`);
        if (response.status === 200 || response.status === 204) {
          await fetchInvoices();
        }
        setError(null);
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || "Failed to delete invoice.");
        console.error("Error deleting invoice:", err);
      }
    }
  };

  const handleOpenCreateSheet = () => {
    setEditingInvoice(null);
    setIsSheetOpen(true);
  };

  const handleOpenEditSheet = (invoice: Invoice) => {
    setEditingInvoice(invoice);
    setIsSheetOpen(true);
  };

  const filteredInvoices = invoices.filter(
    (i) =>
      i.id.toLowerCase().includes(search.toLowerCase()) ||
      (i.client_id && i.client_id.toLowerCase().includes(search.toLowerCase()))
  );

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  return (
    <div className="flex min-h-screen bg-background overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col transition-all duration-300 lg:ml-64">
        <header className="border-b bg-card px-4 py-3 flex items-center justify-between sticky top-0 z-40">
          <div className="flex items-center gap-3 flex-1">
            <Sheet open={mobileNavOpen} onOpenChange={setMobileNavOpen}>
              <SheetTrigger asChild className="lg:hidden"><Button variant="outline" size="icon"><Menu className="h-5 w-5" /></Button></SheetTrigger>
              <SheetContent side="left" className="p-0 w-64"><SheetHeader className="px-4 py-2 border-b dark:border-gray-800"><SheetTitle>Dashboard Navigation</SheetTitle></SheetHeader><NavigationContent setOpen={setMobileNavOpen} /></SheetContent>
            </Sheet>
            <div className="relative flex-1 max-w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search by Invoice ID or Client ID..." className="pl-10 w-full" value={search} onChange={(e) => setSearch(e.target.value)} />
            </div>
          </div>
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="icon" className="relative"><Bell className="h-4 w-4" /><span className="absolute -top-1 -right-1 h-3.5 w-3.5 bg-destructive rounded-full text-xs flex items-center justify-center">3</span></Button>
            <Button variant="ghost" size="icon" onClick={toggleTheme}>{theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}</Button>
            <Avatar className="cursor-pointer"><AvatarFallback className="bg-primary text-primary-foreground">{typeof window !== 'undefined' ? localStorage.getItem("user_avatar")?.charAt(0).toUpperCase() || 'M' : 'M'}</AvatarFallback></Avatar>
          </div>
        </header>

        <div className="p-6 flex justify-between items-center">
          <div><h1 className="text-2xl font-bold">Invoices</h1><p className="text-muted-foreground">Manage and track all your invoices</p></div>
          <Button onClick={handleOpenCreateSheet} className="bg-blue-600 hover:bg-blue-700 text-white"><Plus className="w-4 h-4 mr-2" />Create Invoice</Button>
        </div>

        <div className="px-6 pb-6 flex-1 overflow-y-auto">
          {loading ? <p className="text-center">Loading...</p> : error ? <p className="text-center text-destructive">{error}</p> : (
            <div className="border rounded-lg">
              <table className="w-full text-sm">
                <thead className="bg-muted/50"><tr className="text-left text-muted-foreground"><th className="p-3">Invoice ID</th><th className="p-3">Client ID</th><th className="p-3">Date</th><th className="p-3">Amount</th><th className="p-3">Status</th><th className="p-3 text-right">Actions</th></tr></thead>
                <tbody>
                  {filteredInvoices.length > 0 ? filteredInvoices.map((invoice) => (
                    <tr key={invoice.id} className="border-b hover:bg-muted/50">
                      <td className="p-3 font-mono text-xs">{invoice.id}</td>
                      <td className="p-3 font-mono text-xs">{invoice.client_id || 'N/A'}</td>
                      <td className="p-3">{formatDate(invoice.invoice_date)}</td>
                      <td className="p-3">Rs {invoice.total_amount.toLocaleString()}</td>
                      <td className="p-3">
                        <span className={`px-2 py-1 rounded-full text-xs ${invoice.payment_status === "paid" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}`}>
                          {invoice.payment_status || 'unknown'}
                        </span>
                      </td>
                      <td className="p-3 text-right">
                        <div className="relative inline-block">
                          <Sheet>
                            <SheetTrigger asChild>
                               <Button variant="ghost" size="icon" onClick={() => handleOpenEditSheet(invoice)}><Edit className="h-4 w-4" /></Button>
                            </SheetTrigger>
                          </Sheet>
                           <Button variant="ghost" size="icon" onClick={() => handleDeleteInvoice(invoice.id)}><Trash2 className="h-4 w-4 text-destructive" /></Button>
                        </div>
                      </td>
                    </tr>
                  )) : <tr><td colSpan={6} className="p-6 text-center text-muted-foreground">No invoices found.</td></tr>}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
        <SheetContent>
          <SheetHeader><SheetTitle>{editingInvoice ? 'Edit Invoice' : 'Create New Invoice'}</SheetTitle></SheetHeader>
          <div className="py-4">
            <InvoiceForm
              onSubmit={handleFormSubmit}
              onCancel={() => setIsSheetOpen(false)}
              initialData={editingInvoice}
            />
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}