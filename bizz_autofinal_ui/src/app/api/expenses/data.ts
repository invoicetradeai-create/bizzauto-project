// Simple in-memory data store for development
type PaymentMethod = 'Cash' | 'Bank Transfer' | 'Credit Card' | 'Debit Card';

export interface DailyExpense {
  id: number;
  date: string; // YYYY-MM-DD
  description: string;
  category: string;
  amount: number;
  paymentMethod: PaymentMethod | string;
  receipt: boolean;
}

let expenses: DailyExpense[] = [
  { id: 1, date: '2025-11-03', description: 'Fuel for delivery truck', category: 'Fuel', amount: 5000, paymentMethod: 'Cash', receipt: true },
  { id: 2, date: '2025-11-02', description: 'Office supplies', category: 'Office Supplies', amount: 1200, paymentMethod: 'Bank Transfer', receipt: false },
];

export function getAll() {
  return expenses;
}

export function addExpense(item: Omit<DailyExpense, 'id'>) {
  const id = expenses.length ? Math.max(...expenses.map(e => e.id)) + 1 : 1;
  const newItem: DailyExpense = { id, ...item };
  expenses = [newItem, ...expenses];
  return newItem;
}

export function deleteExpense(id: number) {
  const exists = expenses.some(e => e.id === id);
  expenses = expenses.filter(e => e.id !== id);
  return exists;
}

export function updateExpense(id: number, patch: Partial<DailyExpense>) {
  let updated: DailyExpense | undefined;
  expenses = expenses.map(e => {
    if (e.id === id) {
      updated = { ...e, ...patch };
      return updated!;
    }
    return e;
  });
  return updated;
}

export function getSummary() {
  const today = new Date().toISOString().split('T')[0];
  const now = new Date();
  const month = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`; // YYYY-MM
  const year = now.getFullYear().toString();

  const sumToday = expenses.filter(e => e.date === today).reduce((s, e) => s + e.amount, 0);
  const sumMonth = expenses.filter(e => e.date.startsWith(month)).reduce((s, e) => s + e.amount, 0);
  const sumYear = expenses.filter(e => e.date.startsWith(year)).reduce((s, e) => s + e.amount, 0);

  return { today: sumToday, month: sumMonth, year: sumYear };
}

export function toCSV() {
  const header = ['id', 'date', 'description', 'category', 'amount', 'paymentMethod', 'receipt'];
  const rows = expenses.map(e => [e.id, e.date, `"${String(e.description).replace(/"/g, '""')}"`, e.category, e.amount, e.paymentMethod, e.receipt]);
  const csv = [header, ...rows].map(r => r.join(',')).join('\n');
  return csv;
}
