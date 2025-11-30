import axios from "axios";

const baseURL = process.env.NEXT_PUBLIC_API_URL || "https://bizzauto-project.onrender.com";
console.log("🚀 API Client Base URL:", baseURL);

const apiClient = axios.create({
  baseURL: baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

import { supabase } from "@/lib/supabaseClient";

apiClient.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession();
  if (session?.access_token) {
    config.headers["Authorization"] = `Bearer ${session.access_token}`;
  }
  return config;
});

export { apiClient };
