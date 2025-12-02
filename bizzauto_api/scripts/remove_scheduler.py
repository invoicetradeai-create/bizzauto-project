import os

file_path = r"e:\aptech bizz auto\bizz auto project\bizzauto-project\bizzauto_api\main.py"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "Start Scheduler Worker in Background" in line:
        skip = True
        continue
    if skip and "logging.error" in line and "Failed to start scheduler worker" in line:
        skip = False
        continue
    if skip:
        continue
    new_lines.append(line)

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Successfully removed scheduler startup block.")
