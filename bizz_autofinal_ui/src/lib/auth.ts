import { supabase } from "@/lib/supabaseClient";


export const getAuthToken = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token;
};

export const getAuthHeaders = async (): Promise<HeadersInit> => {
    const token = await getAuthToken();
    return token ? { "Authorization": `Bearer ${token}` } : {};
};
