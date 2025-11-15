import { NextResponse } from 'next/server';
import { toCSV } from '../data';

export async function GET(req: Request) {
  try {
    const url = new URL(req.url);
    const format = url.searchParams.get('format') || 'csv';
    if (format === 'csv') {
      const csv = toCSV();
      return new NextResponse(csv, {
        status: 200,
        headers: {
          'Content-Type': 'text/csv; charset=utf-8',
          'Content-Disposition': 'attachment; filename="expenses.csv"',
        },
      });
    }
    // For other formats just return 204 for now
    return NextResponse.json({ message: 'Not implemented' }, { status: 204 });
  } catch (err) {
    return NextResponse.json({ error: 'Export failed' }, { status: 500 });
  }
}
