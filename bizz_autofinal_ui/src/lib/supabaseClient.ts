import { createClient } from "@supabase/supabase-js";

// ✅ Correct syntax for Next.js
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
    throw new Error("Supabase URL and Key are required. Check your .env.local file.");
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
console.log("✅ Supabase URL:", supabaseUrl, "Type:", typeof supabaseUrl, "Length:", supabaseUrl?.length);
console.log("✅ Supabase Key:", supabaseAnonKey ? "Loaded" : "Missing", "Type:", typeof supabaseAnonKey, "Length:", supabaseAnonKey?.length);
