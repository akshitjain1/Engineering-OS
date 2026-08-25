"""Add ratio and subject_progress functions to curriculum.py."""

with open('D:/Akshit Personal OS/backend/app/curriculum.py', 'r') as f:
    content = f.read()

# Add the two missing functions at the end
add_funcs = '''

def ratio(completed: int, total: int) -> float:
    return round(completed / total * 100, 1) if total > 0 else 0

def subject_progress(items: list[dict[str, Any]], total: int) -> dict[str, Any]:
    completed = sum(1 for i in items if i.get('complete', False))
    return {"completed": completed, "total": total, "percentage": round(completed / total * 100, 1) if total > 0 else 0}

'''

if 'def ratio' not in content:
    content = content.rstrip() + add_funcs
    with open('D:/Akshit Personal OS/backend/app/curriculum.py', 'w') as f:
        f.write(content)
    print('Functions added')
else:
    print('Functions already exist')