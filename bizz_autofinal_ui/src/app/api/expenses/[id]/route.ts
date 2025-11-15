import { NextResponse, NextRequest } from 'next/server';
import { deleteExpense, updateExpense } from '../data';

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const id = Number(params.id);
    console.log('[api/expenses DELETE] incoming id=', id);
    const ok = deleteExpense(id);
    console.log('[api/expenses DELETE] delete result=', ok);
    if (!ok) return NextResponse.json({ error: 'Not found' }, { status: 404 });
    return NextResponse.json({ success: true }, { status: 200 });
  } catch (err) {
    return NextResponse.json({ error: 'Delete failed' }, { status: 500 });
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const id = Number(params.id);
    const body = await request.json().catch(() => ({}));
    const patched = updateExpense(id, body);
    if (!patched) return NextResponse.json({ error: 'Not found' }, { status: 404 });
    return NextResponse.json(patched, { status: 200 });
  } catch (err) {
    return NextResponse.json({ error: 'Update failed' }, { status: 500 });
  }
}
