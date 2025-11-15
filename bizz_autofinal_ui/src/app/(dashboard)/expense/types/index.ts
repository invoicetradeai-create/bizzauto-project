
export type PaymentMethod = 'Cash' | 'Bank Transfer' | 'Credit Card' | 'Debit Card';

export interface DailyExpense {
    id: number;
    date: string;
    description: string;
    category: string;
    amount: number;
    paymentMethod: PaymentMethod;
    receipt: boolean;
}

export interface NewExpenseForm {
    date: Date;
    amount: string;
    category: string;
    paymentMethod: string;
    description: string;
    receiptFile: File | null;
}