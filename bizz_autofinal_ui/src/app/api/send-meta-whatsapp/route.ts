
import { NextResponse } from 'next/server';

// This is the URL of your FastAPI backend.
// In a real-world scenario, this should be in an environment variable.
const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

export async function POST(request: Request) {
  try {
    // 1. Get the 'to' and 'body' from the frontend request.
    const { to, body } = await request.json();

    if (!to || !body) {
      return NextResponse.json({ detail: 'Missing "to" or "body" in request' }, { status: 400 });
    }

    // 2. Forward the request to the FastAPI backend.
    const backendResponse = await fetch(`${BACKEND_URL}/api/meta_whatsapp/send-meta-whatsapp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ to, body }),
    });

    // 3. Handle the response from the backend.
    const responseData = await backendResponse.json();

    if (!backendResponse.ok) {
      // If the backend returned an error, forward it to the client.
      return NextResponse.json(
        { detail: responseData.detail || 'An error occurred in the backend.' },
        { status: backendResponse.status }
      );
    }

    // 4. Return the successful response to the frontend.
    return NextResponse.json(responseData, { status: 200 });

  } catch (error: any) {
    console.error('Error in Next.js API route:', error);
    // Handle network errors or other exceptions
    return NextResponse.json({ detail: 'Internal Server Error in Next.js API route.' }, { status: 500 });
  }
}
