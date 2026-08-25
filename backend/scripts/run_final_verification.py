"""RUN FINAL VERIFICATION — canonical closure orchestrator.

Runs, in order:
  1. verify_no_mutation.py            (RULE 1 integrity)
  2. final_curriculum_intelligence_audit.py  (18 checks)
  3. full_curriculum_audit.py         (domain table + reports)
  4. final_acceptance.py              (10 journeys)

Prints the FINAL LOCK VERDICT.
"""
import subprocess
import sys

VENV_PY = r"D:\Akshit Personal OS\backend\venv\Scripts\python.exe"
SCRIPTS = r"D:\Akshit Personal OS\backend\scripts"

STEPS = [
    ("INTEGRITY", "verify_no_mutation.py"),
    ("AUDIT_18", "final_curriculum_intelligence_audit.py"),
    ("FULL_AUDIT", "full_curriculum_audit.py"),
    ("ACCEPTANCE", "final_acceptance.py"),
]

failures = []
for label, script in STEPS:
    print("\n" + "=" * 72)
    print(f"== {label}: {script}")
    print("=" * 72)
    proc = subprocess.run([VENV_PY, rf"{SCRIPTS}\{script}"], cwd=r"D:\Akshit Personal OS\backend")
    if proc.returncode != 0:
        failures.append((label, script))

print("\n" + "=" * 72)
if failures:
    print("FINAL LOCK VERDICT: NOT LOCKED")
    print("Failed stages:", ", ".join(l for l, _ in failures))
    sys.exit(1)
print("FINAL LOCK VERDICT: ENGINEERING OS CURRICULUM — FINAL LOCK PASS")
