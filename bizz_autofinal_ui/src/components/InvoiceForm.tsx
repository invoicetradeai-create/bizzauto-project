"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { UUID } from "crypto";

// Based on the backend Pydantic model
type Invoice = {
  id?: UUID;
  company_id: UUID;
  client_id?: UUID;
  invoice_date: string;
  total_amount: number;
  payment_status?: string;
  notes?: string;
};

interface InvoiceFormProps {
  onSubmit: (invoice: Omit<Invoice, 'id' | 'company_id'>) => void;
  onCancel: () => void;
  initialData?: Invoice | null;
}

export default function InvoiceForm({ onSubmit, onCancel, initialData }: InvoiceFormProps) {
  const [formData, setFormData] = useState({
    client_id: initialData?.client_id || '',
    invoice_date: initialData?.invoice_date ? new Date(initialData.invoice_date).toISOString().split('T')[0] : new Date().toISOString().split('T')[0],
    total_amount: initialData?.total_amount || 0,
    payment_status: initialData?.payment_status || 'unpaid',
    notes: initialData?.notes || '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (name: string, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Note: company_id will need to be handled outside this form,
    // perhaps from user session or context.
    onSubmit({
      ...formData,
      total_amount: Number(formData.total_amount),
      client_id: formData.client_id as UUID, // Casting for now
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="client_id">Client ID</Label>
        <Input
          id="client_id"
          name="client_id"
          value={formData.client_id}
          onChange={handleChange}
          placeholder="Enter Client UUID"
          required
        />
      </div>
      <div>
        <Label htmlFor="invoice_date">Invoice Date</Label>
        <Input
          id="invoice_date"
          name="invoice_date"
          type="date"
          value={formData.invoice_date}
          onChange={handleChange}
          required
        />
      </div>
      <div>
        <Label htmlFor="total_amount">Total Amount</Label>
        <Input
          id="total_amount"
          name="total_amount"
          type="number"
          value={formData.total_amount}
          onChange={handleChange}
          required
        />
      </div>
      <div>
        <Label htmlFor="payment_status">Payment Status</Label>
        <Select
          name="payment_status"
          value={formData.payment_status}
          onValueChange={(value) => handleSelectChange('payment_status', value)}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="unpaid">Unpaid</SelectItem>
            <SelectItem value="paid">Paid</SelectItem>
            <SelectItem value="partial">Partial</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div>
        <Label htmlFor="notes">Notes</Label>
        <Textarea
          id="notes"
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          placeholder="Optional notes about the invoice"
        />
      </div>
      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit">
          {initialData ? 'Update Invoice' : 'Create Invoice'}
        </Button>
      </div>
    </form>
  );
}
