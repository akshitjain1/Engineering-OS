"""Restore evaluate_prerequisites to original form."""
with open('D:/Akshit Personal OS/backend/app/curriculum.py', 'r') as f:
    content = f.read()

start_marker = 'def evaluate_prerequisites('
start_idx = content.find(start_marker)
if start_idx >= 0:
    # Find end - next def at column 0
    remaining = content[start_idx:]
    lines = remaining.split('\n')
    end_idx = len(lines)
    for i, line in enumerate(lines):
        # A top-level def has no leading whitespace or just one space (method in class)
        # We want the one at the module level (no class indentation)
        lstripped = line.lstrip()
        if lstripped.startswith('def ') and not any(lstripped.startswith(prefix) for prefix in ['    ', '        ', '            ']):
            end_idx = i
            break
    
    if end_idx < len(lines):
        # Take everything before the new def
        before = '\n'.join(lines[:end_idx])
        after = '\n'.join(lines[end_idx:])
        new_content = before + original_func + '\n' + after
        with open('D:/Akshit Personal OS/backend/app/curriculum.py', 'w') as f:
            f.write(new_content)
        print('Restored evaluate_prerequisites')
    else:
        print('Could not find end boundary')
else:
    print('Could not find evaluate_prerequisites start')