import os

file_path = r"e:\aptech bizz auto\bizz auto project\bizzauto-project\bizzauto_api\routers\api\meta_whatsapp.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix the specific argument mismatch
new_content = content.replace("send_reply(to=sender_phone, message=reply)", "send_reply(to=sender_phone, data=reply)")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Fixed send_reply argument in meta_whatsapp.py")
