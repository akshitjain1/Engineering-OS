with open('D:/Akshit Personal OS/backend/app/content/resources.py', 'r') as f:
    content = f.read()

new_func = "\n\ndef lesson_ui_status(completion_status):\n    normalized = (completion_status or 'not_started').lower()\n    if normalized in ('complete', 'completed', 'done'):\n        return 'complete'\n    if normalized in ('in progress', 'not started'):\n        return 'in progress'\n    return 'not_started'\n"

new_content = content + new_func

with open('D:/Akshit Personal OS/backend/app/content/resources.py', 'w') as f:
    f.write(new_content)
print('Added lesson_ui_status')