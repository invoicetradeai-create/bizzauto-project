import { createClient } from "@supabase/supabase-js";

// ✅ Correct syntax for Next.js
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
console.log("✅ Supabase URL:", process.env.NEXT_PUBLIC_SUPABASE_URL);
console.log("✅ Supabase Key:", process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ? "Loaded" : "Missing");
