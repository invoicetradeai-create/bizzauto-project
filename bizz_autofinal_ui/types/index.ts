// bizz_autofinal_ui/types/index.ts

export interface Invoice {
  id?: string;
  company_id: string;
  client_id?: string;
  invoice_date: string;
  total_amount: number;
  payment_status?: string;
  notes?: string;
  items?: any[]; // Assuming invoice items might be nested
}

export interface Client {
  id?: string;
  company_id: string;
  name: string;
  phone?: string;
  email?: string;
  address?: string;
}

export interface Product {
  id?: string;
  company_id: string;
  name: string;
  sku?: string;
  category?: string;
  purchase_price?: number;
  sale_price?: number;
  stock_quantity?: number;
  low_stock_alert?: number;
  unit?: string;
}

export interface WhatsappLog {
  id?: string;
  company_id: string;
  message_type?: string;
  phone?: string;
  message?: string;
  status?: string;
  created_at?: string; // Assuming a created_at field for date processing
}
