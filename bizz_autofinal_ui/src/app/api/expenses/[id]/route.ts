import { NextResponse, NextRequest } from 'next/server';
import { deleteExpense, updateExpense } from '../data';

export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ id: string }> } // Changed to Promise
) {
  try {
    const { id } = await context.params; // Await the params
    const numericId = Number(id);
    console.log('[api/expenses DELETE] incoming id=', numericId);
    const ok = deleteExpense(numericId);
    console.log('[api/expenses DELETE] delete result=', ok);
    if (!ok) return NextResponse.json({ error: 'Not found' }, { status: 404 });
    return NextResponse.json({ success: true }, { status: 200 });
  } catch (err) {
    return NextResponse.json({ error: 'Delete failed' }, { status: 500 });
  }
}

export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ id: string }> } // Changed to Promise
) {
  try {
    const { id } = await context.params; // Await the params
    const numericId = Number(id);
    const body = await request.json().catch(() => ({}));
    const patched = updateExpense(numericId, body);
    if (!patched) return NextResponse.json({ error: 'Not found' }, { status: 404 });
    return NextResponse.json(patched, { status: 200 });
  } catch (err) {
    return NextResponse.json({ error: 'Update failed' }, { status: 500 });
  }
}