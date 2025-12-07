import os

file_path = r"e:\aptech bizz auto\bizz auto project\bizzauto-project\bizz_autofinal_ui\.env.local"

content = """NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_SUPABASE_URL=https://izouggmchawwoltlerlg.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml6b3VnZ21jaGF3d29sdGxlcmxnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI0NTMxMTMsImV4cCI6MjA3ODAyOTExM30.IX_JFXPvxa1r0qs2tIfhFSQxVzY4D46s3ZdLRpkgq3U
"""

try:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully wrote .env.local with UTF-8 encoding.")
except Exception as e:
    print(f"Error writing file: {e}")
