import os

file_path = r"e:\aptech bizz auto\bizz auto project\bizzauto-project\bizz_autofinal_ui\.env.local"

try:
    with open(file_path, 'r', encoding='utf-16') as f:
        content = f.read()
        
    recovered = ""
    for char in content:
        val = ord(char)
        # Little Endian: low byte first, then high byte
        low = val & 0xFF
        high = (val >> 8) & 0xFF
        
        if low:
            recovered += chr(low)
        if high:
            recovered += chr(high)
            
    print("--- Recovered Content ---")
    print(recovered)
    
except Exception as e:
    print(f"Recovery failed: {e}")
