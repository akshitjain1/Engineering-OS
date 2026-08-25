with open('D:/Akshit Personal OS/backend/app/content/resources.py', 'r') as f:
    content = f.read()

old = "def lesson_ui_status(completion_status):"
new = "def lesson_ui_status(completion_status, progress=None):"

new_content = content.replace(old, new)

with open('D:/Akshit Personal OS/backend/app/content/resources.py', 'w') as f:
    f.write(new_content)
print('Updated lesson_ui_status signature')