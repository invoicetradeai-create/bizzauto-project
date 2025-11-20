// API Configuration
export const API_CONFIG = {
  // BASE_URL should point directly to the FastAPI backend
  BASE_URL: (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, ''), // remove trailing slash
  TIMEOUT: 30000,
};

// API Endpoints (always start with ONLY one slash)
export const API_ENDPOINTS = {
  // Health check
  health: '/health',

  // Companies
  companies: '/api/companies',

  // Clients
  clients: '/api/clients',

  // Products
  products: '/api/products',

  // Invoices
  invoices: '/api/invoices',
  invoiceItems: '/api/invoice_items',

  // Purchases
  purchases: '/api/purchases',
  purchaseItems: '/api/purchase_items',

  // Expenses
  expenses: '/api/expenses',

  // Others
  suppliers: '/api/suppliers',
  leads: '/api/leads',
  users: '/api/users',
  whatsappLogs: '/api/whatsapp_logs',
  uploadedDocs: '/api/uploaded_docs',
  settings: '/api/settings',

  // Meta WhatsApp
  // This now points directly to the FastAPI endpoint
  sendMetaWhatsapp: '/api/meta_whatsapp/send-meta-whatsapp',
  scheduledWhatsappMessages: '/api/scheduled-whatsapp-messages',

  // Dashboard
  dashboard: '/dashboard',
};
