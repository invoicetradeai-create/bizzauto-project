import os

file_path = r"e:\aptech bizz auto\bizz auto project\bizzauto-project\bizzauto_api\.env"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix the specific typo
new_content = content.replace("aws-1-ap-sout heast-1", "aws-1-ap-southeast-1")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Fixed DATABASE_URL in .env")
