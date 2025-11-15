import { NextResponse } from 'next/server';
import { addExpense } from '../data';

type Payload = {
  date?: unknown;
  amount?: unknown;
  category?: unknown;
  paymentMethod?: unknown;
  description?: unknown;
  receipt?: unknown;
  [k: string]: unknown;
};

export async function POST(req: Request) {
  try {
    // Support form-data and JSON
    let payload: Payload = {};
    const contentType = req.headers.get('content-type') || '';
    if (contentType.includes('multipart/form-data')) {
      const form = await req.formData();
      payload.date = String(form.get('date') || new Date().toISOString()).split('T')[0];
      payload.amount = Number(form.get('amount') || 0);
      payload.category = String(form.get('category') || '');
      payload.paymentMethod = String(form.get('paymentMethod') || '');
      payload.description = String(form.get('description') || '');
      payload.receipt = !!form.get('receipt');
    } else {
      payload = (await req.json().catch(() => ({}))) as Payload;
      if (payload.date) payload.date = String(payload.date).split('T')[0];
    }

    const created = addExpense({
      date: String(payload.date ?? new Date().toISOString()).split('T')[0],
      description: String(payload.description ?? ''),
      category: String(payload.category ?? ''),
      amount: Number(payload.amount) || 0,
      paymentMethod: String(payload.paymentMethod ?? 'Cash'),
      receipt: !!payload.receipt,
    });

    return NextResponse.json(created, { status: 201 });
  } catch (err) {
    return NextResponse.json({ error: 'Failed to create' }, { status: 500 });
  }
}
