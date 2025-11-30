import os

file_path = r"e:\aptech bizz auto\bizz auto project\bizzauto-project\bizz_autofinal_ui\.env.local"

try:
    with open(file_path, 'r', encoding='utf-16') as f:
        content = f.read()
        print("--- Decoded with UTF-16 ---")
        print(content)
except Exception as e:
    print(f"UTF-16 failed: {e}")

try:
    with open(file_path, 'r', encoding='utf-16-le') as f:
        content = f.read()
        print("--- Decoded with UTF-16-LE ---")
        print(content)
except Exception as e:
    print(f"UTF-16-LE failed: {e}")
