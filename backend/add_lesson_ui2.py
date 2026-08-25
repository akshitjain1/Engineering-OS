with open('D:/Akshit Personal OS/backend/app/content/resources.py', 'r') as f:
    content = f.read()

new_func = \"\"\"def lesson_ui_status(completion_status: str | None) -> str:
    normalized = (completion_status or \"not_started\").lower()
    if normalized in (\"complete\", \"completed\", \"done\"):
        return \"complete\"
    if normalized in (\"in progress\", \"not started\"):
        return \"in progress\"
    return \"not_started\"

\"\"\"

# Insert after line 21 (after ACTIVE_PRIMARY_STATUSES)
lines = content.split(\"\\n\")
insert_idx = 22  # after line 21
new_lines = lines[:insert_idx] + [new_func] + lines[insert_idx:]
new_content = \"\\n\".join(new_lines)

with open('D:/Akshit Personal OS/backend/app/content/resources.py', 'w') as f:
    f.write(new_content)
print('Added lesson_ui_status')