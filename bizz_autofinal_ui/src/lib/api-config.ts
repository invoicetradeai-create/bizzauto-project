// bizz_autofinal_ui/src/lib/api-config.ts
export const API_ENDPOINTS = {
  clients: '/api/clients',
  companies: '/api/companies',
  products: '/api/products',
  invoices: '/api/invoice-processing/invoices',
  invoiceUpload: '/api/invoice-processing/upload-invoice', // For file uploads
  invoice: '/api/invoice-processing/invoice', // For manual CRUD
  expenses: '/api/expenses',
  whatsappLogs: '/api/whatsapp_logs',
  scheduledWhatsappMessages: '/api/scheduled-whatsapp-messages',
  sendMetaWhatsapp: '/api/meta_whatsapp/send-meta-whatsapp',
  health: '/health',
  accounting: {
    sales_summary: '/api/accounting/sales_summary',
    expense_report: '/api/accounting/expense_report',
    stock_report: '/api/accounting/stock_report',
  },
  adminBilling: '/api/admin/billing',
};