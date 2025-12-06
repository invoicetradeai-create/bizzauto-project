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

  useEffect(() => {
    fetchExpenses();
    fetchSummary();
  }, []);

  const fetchExpenses = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/expenses/all');
      if (!res.ok) throw new Error('Failed to fetch');
      const data: DailyExpense[] = await res.json();
      setExpenses(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      const res = await fetch('/api/expenses/summary');
      if (!res.ok) return;
      const data = await res.json();
      setSummary(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { id, value } = e.target;
    setForm((prev) => ({ ...prev, [id]: value }));
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
      const fd = new FormData();
      fd.append('date', form.date.toISOString());
      fd.append('amount', form.amount);
      fd.append('category', form.category);
      fd.append('paymentMethod', form.paymentMethod);
      fd.append('description', form.description);
      if (form.receiptFile) fd.append('receipt', form.receiptFile);

      const res = await fetch('/api/expenses/add', { method: 'POST', body: fd });
      if (!res.ok) throw new Error('Failed to add');
      const added: DailyExpense = await res.json();
      setExpenses(prev => [added, ...prev]);
      setForm({ date: new Date(), amount: '', category: '', paymentMethod: '', description: '', receiptFile: null, clientPhoneNumber: '' });
      await fetchSummary();
      toast.success("Expense added successfully!"); // Add success toast
    } catch (err) {
      console.error(err);
      toast.error(`Failed to add expense: ${err instanceof Error ? err.message : String(err)}`); // Use toast for error
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this expense?')) return;
    try {
      const res = await fetch(`/api/expenses/${id}`, { method: 'DELETE' });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ message: 'Failed to delete' }));
        throw new Error(errorData.message);
      }
      setExpenses(prev => prev.filter(p => p.id !== id));
      await fetchSummary();
    } catch (err) {
      console.error('[frontend] delete error:', err);
      alert(`Failed to delete: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  const handleExport = async (format: 'pdf') => {
    setExportingPDF(true);
    try {
      const res = await fetch(`/api/expenses/export?format=${format}`);
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
          <h3 className="font-semibold mb-4 text-lg">Add New Expense</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="description">Description</label>
              <Input id="description" value={form.description} onChange={handleInput} placeholder="e.g., Fuel for delivery truck" />
            </div>
            <div>
              <label htmlFor="category">Category</label>
              <Select onValueChange={(val: string) => setForm({ ...form, category: val })}><SelectTrigger><SelectValue placeholder="Select category" /></SelectTrigger><SelectContent>{expenseCategories.map((cat) => <SelectItem key={cat} value={cat}>{cat}</SelectItem>)}</SelectContent></Select>
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
              <Select onValueChange={(val: string) => setForm({ ...form, paymentMethod: val })}><SelectTrigger><SelectValue placeholder="Select method" /></SelectTrigger><SelectContent>{paymentMethods.map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}</SelectContent></Select>
            </div>
            <div>
              <label htmlFor="clientPhoneNumber">Client WhatsApp Number</label>
              <Input id="clientPhoneNumber" value={form.clientPhoneNumber} onChange={handleInput} placeholder="923001234567" />
            </div>
            <div className="flex flex-col sm:flex-row sm:flex-wrap justify-end gap-2">
              <Button type="submit" className="w-full sm:w-auto"><Plus className="w-4 h-4 mr-2" /> Add Expense</Button>
              <Button type="button" onClick={handleSendExpenseReportWhatsApp} disabled={sendingWhatsApp || !form.clientPhoneNumber} className="w-full sm:w-auto">
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
                      <Button variant="ghost" size="icon"><PenSquare className="w-4 h-4" /></Button>
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
