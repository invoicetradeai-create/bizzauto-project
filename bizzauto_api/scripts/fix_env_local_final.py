import os

env_path = r"e:\aptech bizz auto\bizz auto project\bizzauto-project\bizz_autofinal_ui\.env.local"

content = "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000\n"

try:
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully wrote to {env_path}")
    
    # Verify
    with open(env_path, "r", encoding="utf-8") as f:
        print("Verification read:")
        print(f.read())
        
except Exception as e:
    print(f"Error: {e}")
