import os

file_path = r"e:\aptech bizz auto\bizz auto project\bizzauto-project\bizz_autofinal_ui\.env.local"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print("--- Decoded with UTF-8 ---")
        print(content)
except Exception as e:
    print(f"UTF-8 failed: {e}")
