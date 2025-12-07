"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useTheme } from "@/hooks/use-theme";
import { Button } from "@/components/ui/button";
import { Moon, Sun, Bell, Menu, Search, Upload, Plus, MoreHorizontal, Trash2, Edit, RefreshCw } from "lucide-react"; // Added RefreshCw for refresh icon
import Sidebar, { NavigationContent } from "@/components/Sidebar";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"; // New table components

import InvoiceForm from "@/components/InvoiceForm";
import OcrUploadDialog from "@/components/OcrUploadDialog"; // Keep local OCR import
import { UUID } from "crypto";
import { apiClient } from "@/lib/api-client";
import { API_ENDPOINTS } from "@/lib/api-config"; // Adopt API_ENDPOINTS
import { format as formatDateFns } from "date-fns"; // Adopt date-fns

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
  const router = useRouter();
  const { theme, toggleTheme, mounted } = useTheme();
  const [search, setSearch] = useState("");
  const [open, setOpen] = useState(false); // Mobile sidebar state, renamed from mobileNavOpen
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [isOcrDialogOpen, setIsOcrDialogOpen] = useState(false); // Keep local OCR state
  
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  const [editingInvoice, setEditingInvoice] = useState<Invoice | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0); // New state to trigger data refresh

  const fetchInvoices = useCallback(async () => {
    console.log(`🔄 Fetching invoices (trigger: ${refreshTrigger})...`);
    setLoading(true);
    setError(null);
    try {
      const endpoint = API_ENDPOINTS.invoices; // Use the corrected endpoint
      console.log(`📡 Calling API: ${endpoint}`);
      const response = await apiClient.get<Invoice[]>(endpoint);
      setInvoices(response.data);
      console.log("✅ Invoices fetched successfully:", response.data.length, "items");
      console.log("Raw Invoices API Response Data:", response.data); // Log raw response data
    } catch (err: any) {
      const errorMessage = `Failed to fetch invoices: ${err.message || err}`;
      setError(errorMessage);
      console.error("❌ Error fetching invoices:", err.response?.data || err);
    } finally {
      setLoading(false);
    }
  }, [setInvoices, setError, setLoading, apiClient, refreshTrigger]); // Added refreshTrigger to dependencies

  useEffect(() => {
    fetchInvoices();
  }, [fetchInvoices]); // Depend on fetchInvoices, which now depends on refreshTrigger

  const handleFormSubmit = async (invoiceData: Omit<Invoice, 'id' | 'company_id'>) => {
    try {
      if (editingInvoice) {
        // Update logic - Adopt remote's API endpoint
        console.log(`⬆️ Updating invoice: ${editingInvoice.id} with data:`, invoiceData);
        await apiClient.put<Invoice>(`/api/invoice-processing/invoice/${editingInvoice.id}`, invoiceData);
        console.log("✅ Invoice updated successfully.");
      } else {
        // Create logic - Adopt remote's API endpoint
        console.log("➕ Creating new invoice with data:", invoiceData);
        await apiClient.post<Invoice>(API_ENDPOINTS.invoice, invoiceData); // Use manual invoice creation endpoint
        console.log("✅ Invoice created successfully.");
      }
      setIsSheetOpen(false);
      setEditingInvoice(null);
      setRefreshTrigger(prev => prev + 1); // Trigger data refresh
      console.log("🔄 Triggered invoice data refresh.");
      setError(null); // Clear any previous errors on successful submit
    } catch (err: any) {
      let errorMessage = err.message || (editingInvoice ? "Failed to update invoice." : "Failed to create invoice.");
      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail.map((e: any) => e.msg).join(", ");
        } else {
          errorMessage = err.response.data.detail;
        }
      }
      setError(errorMessage);
      console.error("❌ Error submitting invoice:", err.response?.data || err);
    }
  };

  const handleDeleteInvoice = async (invoiceId: UUID) => {
    if (window.confirm("Are you sure you want to delete this invoice?")) {
      try {
        // Adopt remote's API endpoint
        console.log(`🗑️ Deleting invoice: ${invoiceId}`);
        const response = await apiClient.delete(`/api/invoice-processing/invoice/${invoiceId}`);
        if (response.status === 200 || response.status === 204) {
          console.log("✅ Invoice deleted successfully.");
          setRefreshTrigger(prev => prev + 1); // Trigger data refresh
          console.log("🔄 Triggered invoice data refresh.");
        }
        setError(null);
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || "Failed to delete invoice.");
        console.error("❌ Error deleting invoice:", err.response?.data || err);
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

  const handleUploadSuccess = () => { // Keep local OCR function
    fetchInvoices();
  };

  const filteredInvoices = useMemo(() => {
    return invoices.filter(
      (i) =>
        i.id.toLowerCase().includes(search.toLowerCase()) ||
        (i.client_id && i.client_id.toLowerCase().includes(search.toLowerCase()))
    );
  }, [invoices, search]);

  const formatDate = (dateString: string) => { // Adopt date-fns formatDate
    return formatDateFns(new Date(dateString), "PPP");
  };

  return (
    <div className="flex min-h-screen bg-background overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col transition-all duration-300 lg:ml-64 overflow-x-hidden">
        <header className="border-b bg-card px-2 py-2 sm:px-4 sm:py-3 lg:px-6 lg:py-4 flex items-center justify-between sticky top-0 z-40">
          <div className="flex items-center gap-3 flex-1">
            <Sheet open={open} onOpenChange={setOpen}>
              <SheetTrigger asChild className="lg:hidden"><Button variant="outline" size="icon"><Menu className="h-5 w-5" /></Button></SheetTrigger>
              <SheetContent side="left" className="p-0 w-64"><SheetHeader className="px-4 py-2 border-b dark:border-gray-800"><SheetTitle>Dashboard Navigation</SheetTitle></SheetHeader><NavigationContent setOpen={setOpen} /></SheetContent>
            </Sheet>
            <div className="relative flex-1 max-w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search by Invoice ID or Client ID..." className="pl-10 w-full" value={search} onChange={(e) => setSearch(e.target.value)} />
            </div>
          </div>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setRefreshTrigger(prev => prev + 1)} // Refresh button
              className="hover:bg-blue-50 dark:hover:bg-gray-800 transition p-[5px]"
              title="Refresh Invoices"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" className="relative"><Bell className="h-4 w-4" /><span className="absolute -top-1 -right-1 h-3.5 w-3.5 bg-destructive rounded-full text-xs flex items-center justify-center">3</span></Button>
            <Button variant="ghost" size="icon" onClick={toggleTheme}>{mounted && theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}</Button>
            <div onClick={() => router.push('/settings')} className="cursor-pointer hover:scale-105 transition-transform duration-200">
              <Avatar>
                <AvatarFallback className="bg-primary text-primary-foreground">{mounted ? localStorage.getItem("user_avatar")?.charAt(0).toUpperCase() || 'M' : 'M'}</AvatarFallback>
              </Avatar>
            </div>
          </div>
        </header>

        <div className="p-4 md:p-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div><h1 className="text-xl md:text-2xl font-bold">Invoices</h1><p className="text-muted-foreground text-sm md:text-base">Manage and track all your invoices</p></div>
          <div className="flex gap-2">
            <Button onClick={() => setIsOcrDialogOpen(true)} className="bg-purple-600 hover:bg-purple-700 text-white w-full sm:w-auto"><Upload className="w-4 h-4 mr-2" />Upload Invoice</Button> {/* Keep local OCR Button */}
            <Button onClick={handleOpenCreateSheet} className="bg-blue-600 hover:bg-blue-700 text-white w-full sm:w-auto"><Plus className="w-4 h-4 mr-2" />Create Invoice</Button>
          </div>
        </div>

        <div className="px-4 md:px-6 pb-6 overflow-x-auto">
          {loading ? <p className="text-center">Loading...</p> : error ? <p className="text-center text-destructive">{error}</p> : (
            <div className="w-full bg-card rounded-lg border-border border text-sm overflow-x-auto">
              <Table className="w-full min-w-[800px]">
                <TableHeader className="bg-muted/50"><TableRow className="text-left text-muted-foreground whitespace-nowrap"><TableHead className="p-3">Invoice ID</TableHead><TableHead className="p-3">Client ID</TableHead><TableHead className="p-3">Date</TableHead><TableHead className="p-3">Amount</TableHead><TableHead className="p-3">Status</TableHead><TableHead className="p-3 text-right">Actions</TableHead></TableRow></TableHeader>
                <TableBody>
                  {filteredInvoices.length > 0 ? filteredInvoices.map((invoice) => (
                    <TableRow key={invoice.id} className="border-b hover:bg-muted/50">
                      <TableCell className="p-3 font-mono text-xs">{invoice.id}</TableCell>
                      <TableCell className="p-3 font-mono text-xs">{invoice.client_id || 'N/A'}</TableCell>
                      <TableCell className="p-3">{formatDate(invoice.invoice_date)}</TableCell>
                      <TableCell className="p-3">Rs {invoice.total_amount.toLocaleString()}</TableCell>
                      <TableCell className="p-3">
                        <span className={`px-2 py-1 rounded-full text-xs ${invoice.payment_status === "paid" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}`}>
                          {invoice.payment_status || 'unknown'}
                        </span>
                      </TableCell>
                      <TableCell className="p-3 text-right">
                        <div className="relative inline-block">
                          <Sheet>
                            <SheetTrigger asChild>
                               <Button variant="ghost" size="icon" onClick={() => handleOpenEditSheet(invoice)}><Edit className="h-4 w-4" /></Button>
                            </SheetTrigger>
                          </Sheet>
                           <Button variant="ghost" size="icon" onClick={() => handleDeleteInvoice(invoice.id)}><Trash2 className="h-4 w-4 text-destructive" /></Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  )) : <TableRow><TableCell colSpan={6} className="p-6 text-center text-muted-foreground">No invoices found.</TableCell></TableRow>}
                </TableBody>
              </Table>
            </div>
          )}
        </div>
      </div>

      <Dialog open={isSheetOpen} onOpenChange={setIsSheetOpen}>
        <DialogContent className="w-full max-h-[90vh] overflow-y-auto p-4 sm:p-6 rounded-xl md:max-w-[90%] lg:max-w-xl xl:max-w-2xl">
          <DialogHeader><DialogTitle className="text-xl sm:text-2xl">{editingInvoice ? 'Edit Invoice' : 'Create New Invoice'}</DialogTitle></DialogHeader>
          <div className="py-4">
            <InvoiceForm
              onSubmit={handleFormSubmit}
              onCancel={() => setIsSheetOpen(false)}
              initialData={editingInvoice}
            />
          </div>
        </DialogContent>
      </Dialog>
      <OcrUploadDialog 
        open={isOcrDialogOpen} 
        onOpenChange={setIsOcrDialogOpen} 
        onUploadSuccess={handleUploadSuccess}
        /> {/* Keep local OCR Dialog */}

    </div>
  );
}