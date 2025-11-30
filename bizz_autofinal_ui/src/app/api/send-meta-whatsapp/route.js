
import { NextResponse } from 'next/server';

// This is the URL of your FastAPI backend.
// In a real-world scenario, this should be in an environment variable.
const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

export async function POST(request) {
  try {
    const { to, message_data } = await request.json();

    if (!to || !message_data) {
      return NextResponse.json({ detail: 'Missing "to" or "message_data" in request' }, { status: 400 });
    }

    const backendResponse = await fetch(`${BACKEND_URL}/api/meta_whatsapp/send-meta-whatsapp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ to, message_data }),
    });

    const responseData = await backendResponse.json();

    if (!backendResponse.ok) {
      return NextResponse.json(
        { detail: responseData.detail || 'An error occurred in the backend.' },
        { status: backendResponse.status }
      );
    }

    return NextResponse.json(responseData, { status: 200 });

  } catch (error) {
    console.error('Error in Next.js API route:', error);
    return NextResponse.json({ detail: 'Internal Server Error in Next.js API route.' }, { status: 500 });
  }
}
