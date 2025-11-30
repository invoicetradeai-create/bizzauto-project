const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://izouggmchawwoltlerlg.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml6b3VnZ21jaGF3d29sdGxlcmxnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI0NTMxMTMsImV4cCI6MjA3ODAyOTExM30.IX_JFXPvxa1r0qs2tIfhFSQxVzY4D46s3ZdLRpkgq3U';

const supabase = createClient(supabaseUrl, supabaseKey);

async function testConnection() {
    console.log("Testing connection to:", supabaseUrl);
    try {
        const { data, error } = await supabase.from('users').select('count', { count: 'exact', head: true });
        if (error) {
            console.error("Supabase Error:", error);
        } else {
            console.log("Connection Successful! Data:", data);
        }
    } catch (err) {
        console.error("Network/Client Error:", err);
    }
}

testConnection();
