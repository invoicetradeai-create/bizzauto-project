import { NextResponse } from 'next/server';
import { getAll } from '../data';

export async function GET() {
  try {
    const data = getAll();
    return NextResponse.json(data, { status: 200 });
  } catch (err) {
    return NextResponse.json({ error: 'Internal' }, { status: 500 });
  }
}
