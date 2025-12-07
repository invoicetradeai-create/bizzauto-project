"use client";

import React, { useEffect, useState } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import type { DailyExpense, PaymentMethod, NewExpenseForm } from './types/index';
import toast from 'react-hot-toast';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Trash2, Plus, FileText, Wallet, CalendarDays, Tag, PenSquare } from 'lucide-react';
import { supabase } from '@/lib/supabaseClient';
import { apiClient } from '@/lib/api-client';

const expenseCategories: string[] = ['Fuel', 'Rent', 'Salary', 'Maintenance', 'Office Supplies', 'Transport', 'Marketing'];
const paymentMethods: PaymentMethod[] = ['Cash', 'Bank Transfer', 'Credit Card', 'Debit Card'];

export const DailyExpensesContent: React.FC = () => {
  const [expenses, setExpenses] = useState<DailyExpense[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [summary, setSummary] = useState({ today: 0, month: 0, year: 0 });
  const [exportingPDF, setExportingPDF] = useState(false);
  const [sendingWhatsApp, setSendingWhatsApp] = useState(false);

  const [form, setForm] = useState<NewExpenseForm>({
    date: new Date(),
    amount: '',
    category: '',
    paymentMethod: '',
    description: '',
    receiptFile: null,
    clientPhoneNumber: '',
  });

  const [editingId, setEditingId] = useState<string | null>(null);

  useEffect(() => {
    fetchExpenses();
    fetchSummary();
  }, []);

  const fetchExpenses = async () => {
    setLoading(true);
    try {
      // Use the correct endpoint that exists in the backend
      const response = await apiClient.get('/api/expenses/');
      if (response.data) {
        setExpenses(response.data);
      }
    } catch (err) {
      console.error('Failed to fetch expenses:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      // Use accounting endpoint for expense summary
      const response = await apiClient.get('/api/accounting/expense_report');
      if (response.data) {
        const data = response.data;
        // Calculate summary from the expense report data
        const totalToday = data.reduce((sum: number, expense: any) => {
          const expenseDate = new Date(expense.date || Date.now());
          const today = new Date();
          if (expenseDate.getDate() === today.getDate() &&
              expenseDate.getMonth() === today.getMonth() &&
              expenseDate.getFullYear() === today.getFullYear()) {
            return sum + expense.sum;
          }
          return sum;
        }, 0);

        const totalMonth = data.reduce((sum: number, expense: any) => {
          const expenseDate = new Date(expense.date || Date.now());
          const today = new Date();
          if (expenseDate.getMonth() === today.getMonth() &&
              expenseDate.getFullYear() === today.getFullYear()) {
            return sum + expense.sum;
          }
          return sum;
        }, 0);

        const totalYear = data.reduce((sum: number, expense: any) => {
          const expenseDate = new Date(expense.date || Date.now());
          const today = new Date();
          if (expenseDate.getFullYear() === today.getFullYear()) {
            return sum + expense.sum;
          }
          return sum;
        }, 0);

        setSummary({ today: totalToday, month: totalMonth, year: totalYear });
      }
    } catch (err) {
      console.error('Failed to fetch summary:', err);
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { id, value } = e.target;
    setForm((prev) => ({ ...prev, [id]: value }));
  };

  const handleEdit = (expense: any) => {
    setEditingId(expense.id);
    
    // Safely parse the date. If it fails, default to today.
    let parsedDate = new Date();
    if (expense.date) {
        const d = new Date(expense.date);
        if (!isNaN(d.getTime())) {
            parsedDate = d;
        }
    }

    setForm({
      date: parsedDate,
      amount: expense.amount != null ? expense.amount.toString() : '',
      category: expense.category || '',
      paymentMethod: expense.paymentMethod || '',
      description: expense.description || expense.title || expense.notes || '',
      receiptFile: null,
      clientPhoneNumber: '', // Phone number isn't stored in DailyExpense, reset it
    });
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setForm({
      date: new Date(),
      amount: '',
      category: '',
      paymentMethod: '',
      description: '',
      receiptFile: null,
      clientPhoneNumber: '',
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // --- Validation ---
    if (!form.description.trim()) {
      toast.error("Description cannot be empty.");
      return;
    }
    if (!form.category) {
      toast.error("Please select a category.");
      return;
    }
    const amount = parseFloat(form.amount);
    if (isNaN(amount) || amount <= 0) {
      toast.error("Amount must be a positive number.");
      return;
    }
    if (!form.paymentMethod) {
      toast.error("Please select a payment method.");
      return;
    }
    // --- End Validation ---

    try {
      // Create expense object in the format expected by the backend Pydantic model
      const expenseData = {
        title: form.description, // Backend expects 'title', not 'description'
        category: form.category,
        amount: parseFloat(form.amount), // Convert to number
        expense_date: form.date.toISOString().split('T')[0], // Backend expects 'expense_date' in YYYY-MM-DD format
        notes: form.description // Also use description as notes
        // payment_method is not part of the Expense model, so we don't include it
      };

      if (editingId) {
        // Update existing expense
        const response = await apiClient.put(`/api/expenses/${editingId}`, expenseData);
        if (response.data) {
          const updated: DailyExpense = response.data;
          setExpenses(prev => prev.map(exp => exp.id === editingId ? updated : exp));
          handleCancelEdit(); // Reset form and mode
          await fetchSummary();
          toast.success("Expense updated successfully!");
        }
      } else {
        // Create new expense
        const response = await apiClient.post('/api/expenses/', expenseData);
        if (response.data) {
          const added: DailyExpense = response.data;
          setExpenses(prev => [added, ...prev]);
          handleCancelEdit(); // Reset form
          await fetchSummary();
          toast.success("Expense added successfully!");
        }
      }
    } catch (err) {
      console.error('Failed to save expense:', err);
      toast.error(`Failed to save expense: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this expense?')) return;
    try {
      const response = await apiClient.delete(`/api/expenses/${id}`);
      if (response.status === 200 || response.status === 204) {
        setExpenses(prev => prev.filter(p => p.id !== id));
        await fetchSummary();
      }
    } catch (err) {
      console.error('[frontend] delete error:', err);
      alert(`Failed to delete: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  const handleExport = async (format: 'pdf') => {
    setExportingPDF(true);
    try {
      // For file downloads, we can still use the regular fetch but with proper authentication
      // Since apiClient is primarily for JSON APIs, we'll construct the URL with proper auth if needed
      // For now, we'll keep using fetch but ensure it works with the backend authentication
      const token = localStorage.getItem('access_token'); // Assuming token is stored here
      const headers: Record<string, string> = {
        'Authorization': `Bearer ${token}`
      };

      const res = await fetch(`/api/expenses/export?format=${format}`, {
        headers: token ? headers : {}
      });
      if (!res.ok) throw new Error(`Failed to export ${format}`);
      const blob = await res.blob();
      const filename = `expenses.${format}`;
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      alert(`Successfully exported ${format}!`);
    } catch (err) {
      console.error(`Error exporting ${format}:`, err);
      alert(`Failed to export ${format}: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setExportingPDF(false);
    }
  };

  const formatPhoneNumber = (phone: string) => {
    return phone.replace(/[^0-9]/g, '').replace(/^0+/, '');
  }

const handleSendExpenseReportWhatsApp = async (expense: any) => {
    try {
      // 1. DEFINE PAYLOAD FIRST (Before using it)
      const payload = {
        title: "New Expense",
        amount: Number(expense.amount),
        category: expense.category,
        payment_method: expense.payment_method,
        description: expense.description || "No description",
        date: new Date(expense.date).toISOString().split('T')[0],
        phone: expense.phone || "923001234567" // Fallback if phone is missing
      };

      setSendingWhatsApp(true);

      // 2. NOW LOG IT (This works because 'payload' is defined above)
      console.log("🚀 Sending WhatsApp payload to backend:", payload);

      const { data: { session } } = await supabase.auth.getSession();
      
      // 3. SEND REQUEST
      const response = await apiClient.post("/expenses/send-whatsapp", payload, {
        headers: {
          Authorization: `Bearer ${session?.access_token}`,
        },
      });

      console.log("✅ Backend Response:", response.data);
      alert("WhatsApp message sent successfully!");

    } catch (error: any) {
      console.error("❌ WhatsApp Error Full Object:", error);
      
      if (error.response) {
        // Server responded with an error code (400, 500, etc.)
        console.error("❌ Server Response Data:", error.response.data);
        alert(`Failed: ${error.response.data.detail || "Server Error"}`);
      } else if (error.request) {
        // Request sent but no response
        alert("Network Error: No response from server.");
      } else {
        alert(`Error: ${error.message}`);
      }
    } finally {
      setSendingWhatsApp(false);
    }
  };

  const filtered = expenses.filter(e => {
    if (!search) return true;
    const s = search.toLowerCase();
    return [e.description, e.category, e.paymentMethod, e.date.toString()].join(' ').toLowerCase().includes(s);
  });

  return (
    <div className="flex-1 space-y-6 p-4 sm:p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold">Expense Management</h2>
          <p className="text-sm text-muted-foreground">Track and manage business expenses</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="default" size="sm" onClick={() => handleExport('pdf')} disabled={exportingPDF} className="bg-blue-600 hover:bg-blue-700 text-white">
            <FileText className="w-4 h-4 mr-2" /> {exportingPDF ? 'Downloading...' : 'Download PDF'}
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

        {/* Stat Card: Today */}
        <div className="flex items-center bg-white rounded-lg shadow-md p-5 w-full">
          <div className="p-3 rounded-full bg-blue-100 text-blue-600 text-2xl mr-4 flex-shrink-0">
            <i className="fas fa-calendar-day"></i> {/* Icon for Today */}
          </div>
          <div className="flex flex-col">
            <p className="text-2xl font-bold text-gray-800">Rs {summary.today}</p>
            <p className="text-sm text-gray-500">Today</p>
          </div>
        </div>

        {/* Stat Card: This Month */}
        <div className="flex items-center bg-white rounded-lg shadow-md p-5 w-full">
          <div className="p-3 rounded-full bg-green-100 text-green-600 text-2xl mr-4 flex-shrink-0">
            <i className="fas fa-calendar"></i> {/* Icon for This Month */}
          </div>
          <div className="flex flex-col">
            <p className="text-2xl font-bold text-gray-800">Rs {summary.month}</p>
            <p className="text-sm text-gray-500">This Month</p>
          </div>
        </div>

        {/* Stat Card: This Year */}
        <div className="flex items-center bg-white rounded-lg shadow-md p-5 w-full">
          <div className="p-3 rounded-full bg-purple-100 text-purple-600 text-2xl mr-4 flex-shrink-0">
            <i className="fas fa-calendar-days"></i> {/* Icon for This Year */}
          </div>
          <div className="flex flex-col">
            <p className="text-2xl font-bold text-gray-800">Rs {summary.year}</p>
            <p className="text-sm text-gray-500">This Year</p>
          </div>
        </div>

      </div>

      {/* Add Expense Form & Table */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="p-4 lg:col-span-1">
          <h3 className="font-semibold mb-4 text-lg">{editingId ? 'Edit Expense' : 'Add New Expense'}</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="description">Description</label>
              <Input id="description" value={form.description} onChange={handleInput} placeholder="e.g., Fuel for delivery truck" />
            </div>
            <div>
              <label htmlFor="category">Category</label>
              <Select value={form.category} onValueChange={(val: string) => setForm({ ...form, category: val })}><SelectTrigger><SelectValue placeholder="Select category" /></SelectTrigger><SelectContent>{expenseCategories.map((cat) => <SelectItem key={cat} value={cat}>{cat}</SelectItem>)}</SelectContent></Select>
            </div>
            <div>
              <label htmlFor="amount">Amount</label>
              <Input id="amount" type="number" value={form.amount} onChange={handleInput} placeholder="e.g., 5000" />
            </div>
            <div>
              <label htmlFor="date">Date</label>
              <DatePicker selected={form.date} onChange={(d) => setForm({ ...form, date: d ?? new Date() })} className="w-full rounded-md border border-input bg-transparent px-3 py-2" />
            </div>
            <div>
              <label htmlFor="paymentMethod">Payment Method</label>
              <Select value={form.paymentMethod} onValueChange={(val: string) => setForm({ ...form, paymentMethod: val })}><SelectTrigger><SelectValue placeholder="Select method" /></SelectTrigger><SelectContent>{paymentMethods.map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}</SelectContent></Select>
            </div>
            <div>
              <label htmlFor="clientPhoneNumber">Client WhatsApp Number</label>
              <Input id="clientPhoneNumber" value={form.clientPhoneNumber} onChange={handleInput} placeholder="923001234567" />
            </div>
            <div className="flex flex-col gap-2">
              <Button type="submit" className="w-full">
                {editingId ? <><PenSquare className="w-4 h-4 mr-2" /> Update Expense</> : <><Plus className="w-4 h-4 mr-2" /> Add Expense</>}
              </Button>
              {editingId && (
                <Button type="button" variant="outline" onClick={handleCancelEdit} className="w-full">
                  Cancel Edit
                </Button>
              )}
              <Button type="button" onClick={handleSendExpenseReportWhatsApp} disabled={sendingWhatsApp || !form.clientPhoneNumber} className="w-full mt-2">
                {sendingWhatsApp ? 'Sending...' : 'Send Report via WhatsApp'}
              </Button>
            </div>
          </form>
        </Card>

        <Card className="p-4 lg:col-span-2">
          <div className="flex gap-4 mb-4">
            <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search expenses..." />
            <Button variant="outline">Filter</Button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr><th>Date</th><th>Description</th><th>Category</th><th>Amount</th><th>Payment</th><th>Actions</th></tr></thead>
              <tbody>
                {loading && <tr><td colSpan={6} className="text-center">Loading...</td></tr>}
                {!loading && filtered.map(exp => (
                  <tr key={exp.id}>
                    <td>{new Date(exp.date).toLocaleDateString()}</td>
                    <td>{exp.description}</td>
                    <td>{exp.category}</td>
                    <td>Rs {exp.amount.toFixed(2)}</td>
                    <td>{exp.paymentMethod}</td>
                    <td>
                      <Button variant="ghost" size="icon" onClick={() => handleEdit(exp)}><PenSquare className="w-4 h-4" /></Button>
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(exp.id)}><Trash2 className="w-4 h-4" /></Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
};
