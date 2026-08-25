"""Add missing functions to curriculum.py."""

with open('D:/Akshit Personal OS/backend/app/curriculum.py', 'r') as f:
    content = f.read()

# Check which functions are missing
missing = []
for func_name in ['compose_topic_status', 'module_progress', 'normalize_lesson_state', 
                  'lesson_ui_status', 'is_lesson_complete', 'topic_lesson_progress']:
    if f'def {func_name}' not in content:
        missing.append(func_name)

print('Missing functions:', missing)

if missing:
    # Add the functions at the end of the file
    add_funcs = """
def module_progress(items: list[dict[str, Any]], total: int) -> dict[str, Any]:
    completed = sum(1 for i in items if i.get('complete', False))
    return {"completed": completed, "total": total, "percentage": round(completed / total * 100, 1) if total > 0 else 0}

def normalize_lesson_state(state: str) -> str:
    state = (state or "").lower()
    if state in ("complete", "completed", "done"):
        return "complete"
    if state in ("in progress", "not started"):
        return "in progress"
    return state

def lesson_ui_status(lock: dict[str, Any], progress: dict[str, Any]) -> dict[str, Any]:
    return {
        "locked": lock.get("locked", False),
        "progress_percent": module_progress(lock.get("items", []), lock.get("total", 0)).get("percentage", 0),
        "message": lock.get("message"),
    }

def is_lesson_complete(lock: dict[str, Any], progress: dict[str, Any]) -> bool:
    return lock.get("locked", False) is False and module_progress(lock.get("items", []), lock.get("total", 0)).get("completed", 0) > 0

def topic_lesson_progress(topic: Any, completion: dict[str, Any]) -> dict[str, Any]:
    lock = evaluate_prerequisites(
        topic.prerequisites if topic.prerequisites else [],
        {},
        completion_lookup=completion,
    )
    return lesson_ui_status(lock, {"completed": 0, "total": 0})

def compose_topic_status(locked: bool, lesson_progress: dict[str, Any]) -> str:
    if locked:
        return "locked"
    progress_percent = lesson_progress.get('completed', 0) / max(lesson_progress.get('total', 1), 1) * 100
    if progress_percent >= 80:
        return "complete"
    return "in progress"
"""
    content = content.rstrip() + add_funcs
    with open('D:/Akshit Personal OS/backend/app/curriculum.py', 'w') as f:
        f.write(content)
    print('Functions added')
else:
    print('All functions exist')