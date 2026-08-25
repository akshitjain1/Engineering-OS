"""Fix the evaluate_prerequisites function in curriculum.py."""

import re

with open('D:/Akshit Personal OS/backend/app/curriculum.py', 'r') as f:
    content = f.read()

# The old function starts at def evaluate_prerequisites and ends before the next top-level def
# Find and replace it

# New function text
new_func = '''def evaluate_prerequisites(
    prerequisite_refs: list[str] | None,
    topics_index: dict[str, Any],
    completion_lookup: dict[str, bool] | None = None,
) -> dict[str, Any]:
    refs = [ref for ref in (prerequisite_refs or []) if ref]
    items = []
    missing = []
    for ref in refs:
        slug = _extract_slug_from_ref(ref)
        topic = topics_index.get(slug)
        if topic is None:
            complete = False
            found = False
            display = ref
        else:
            complete = _prereq_complete(topic, completion_lookup)
            found = True
            display = getattr(topic, "name", None) or slug
        items.append({"name": display, "slug": slug, "complete": complete, "found": found})
        if not complete:
            missing.append(display)

    locked = bool(missing)
    if not refs:
        message = None
    elif locked:
        if len(missing) == 1:
            message = f"Complete {missing[0]} to unlock this topic."
        else:
            message = "Complete these topics to unlock: " + ", ".join(missing) + "."
    else:
        message = None

    return {"locked": locked, "message": message, "items": items}'''

# Find the old function and replace it
# Pattern: match from 'def evaluate_prerequisites' to the line before the next top-level def
pattern = r'def evaluate_prerequisites\([^)]*\) -> dict\[str, Any\]:[^}]*return \[{"locked": locked'

# Try a simpler approach: replace the specific lines that are broken
# Let me just replace the whole function by finding its exact location

# Actually, let me just carefully replace the function by locating its start and end
# The function def starts at line 95 in the original, but lines may have shifted

# Let me use a different approach: replace the broken content
# The broken lines are around 95-135

# Find the start of evaluate_prerequisites
start_marker = 'def evaluate_prerequisites('
start_idx = content.find(start_marker)
if start_idx == -1:
    print('Could not find evaluate_prerequisites function')
else:
    # Find the end - look for the next top-level def or class
    remaining = content[start_idx:]
    # Find next def or class at indentation level 0
    end_idx = len(remaining)
    for i, line in enumerate(remaining.split('\n')):
        stripped = line.strip()
        if stripped.startswith('def ') or stripped.startswith('class ') or stripped.startswith('async def '):
            end_idx = sum(1 for _ in range(i))  # line offset
            break
    
    # Actually, let me just directly replace the function by replacing specific known lines
    # The function body starts at line 96 (after def and signature)
    # Let me just replace lines 95-135 area
    
    # Simpler: just replace the function signature + body with the new version
    # Find where the old function ends by looking for the return statement pattern
    
    # Let me take an entirely different approach - just write the corrected file
    pass

# Since the manipulation is getting complex, let me just rewrite the specific section
# by reading the current state and writing a corrected version

print('Starting file repair...')
# Let me just directly fix the known issues

# The function should be from def evaluate_prerequisites through the return statement
# Let me find exact boundaries
lines_list = content.split('\n')
find_start = None
find_end = None

for i, line in enumerate(lines_list):
    if 'def evaluate_prerequisites' in line:
        find_start = i
    if find_start is not None:
        # Check if this line closes the function
        # Look for return statement at indent level same as def
        if 'return {"locked": locked' in line and find_start is not None:
            # Check if the previous non-blank line is at the same indent
            # This is the end of the function
            find_end = i
            break

if find_start is not None and find_end is not None:
    # Replace lines from find_start to find_end (inclusive)
    new_lines = lines[:find_start] + [new_func] + lines[find_end+1:]
    content = '\n'.join(new_lines)
    with open('D:/Akshit Personal OS/backend/app/curriculum.py', 'w') as f:
        f.write(content)
    print('File repaired successfully')
else:
    print('Could not locate function boundaries')
    print('find_start:', find_start)
    print('find_end:', find_end)