
file_path = r"e:\bizz auto finally work last\bizzauto-project\bizzauto_api\routers\api\meta_whatsapp.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

old_str = "reply = await run_whatsapp_agent(incoming_text, sender_phone)"
new_str = "reply = await run_whatsapp_agent(incoming_text, sender_phone, user_id=user_id_for_log)"

if old_str in content:
    new_content = content.replace(old_str, new_str)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully patched meta_whatsapp.py")
else:
    print("Could not find target string in meta_whatsapp.py")
