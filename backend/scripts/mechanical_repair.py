"""MECHANICAL RESOURCE REPAIR — boundary, canonical URL, and provider fixes only.

Applies ONLY deterministic fixes from resource_repair_queue.json:
- 46 BOUNDARY_ONLY_FIX: update boundary metadata
- 134 CANONICAL_URL_FIX: update URL to redirect target
- 3 METADATA_FIX: correct provider/title

Does NOT:
- Replace resources (the 66 RESOURCE_REPLACEMENT_REQUIRED)
- Touch user data (progress, mastery, XP, diagnostics, revision)
- Modify prerequisites or topic graph
- Create new topics or resources
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.db.session import SessionLocal
from app.db.models import (
    CurriculumResource,
    DiagnosticAnswer,
    DiagnosticSession,
    LearningActivity,
    MasteryEvidence,
    RevisionSchedule,
    TopicMastery,
    UserProgress,
    UserXP,
    XpEvent,
)

REPORT_DIR = Path(r"D:\Akshit Personal OS\backend\reports")
REPAIR_QUEUE = json.loads(
    (REPORT_DIR / "resource_repair_queue.json").read_text(encoding="utf-8")
)


def snapshot_learner_data(db):
    """Capture all learner-data counts for before/after comparison."""
    xp_row = db.query(UserXP).first()
    return {
        "user_progress": db.query(UserProgress).count(),
        "topic_mastery": db.query(TopicMastery).count(),
        "mastery_evidence": db.query(MasteryEvidence).count(),
        "user_xp_total": xp_row.total_xp if xp_row else 0,
        "user_xp_level": xp_row.level if xp_row else 0,
        "xp_events": db.query(XpEvent).count(),
        "learning_activities": db.query(LearningActivity).count(),
        "diagnostic_sessions": db.query(DiagnosticSession).count(),
        "diagnostic_answers": db.query(DiagnosticAnswer).count(),
        "revision_schedules": db.query(RevisionSchedule).count(),
    }


# ----------- Title corrections for the 3 provider mismatches ----------
TITLE_CORRECTIONS = {
    "dl-nn-basics-primary": "CS231n — Neural Networks Part 1: Setting up the Architecture",
    "dl-backprop-primary": "CS231n — Backpropagation, Intuitions",
    "dl-cnn-primary": "CS231n — Convolutional Neural Networks",
}


def main():
    db = SessionLocal()
    try:
        # ============================================================
        # PHASE A: Snapshot learner data
        # ============================================================
        print("=" * 70)
        print("PHASE A: Snapshot learner data (pre-change)")
        print("=" * 70)
        before = snapshot_learner_data(db)
        for k, v in before.items():
            print(f"  {k}: {v}")

        # Build resource lookup by slug
        all_resources = db.query(CurriculumResource).all()
        by_slug = {}
        for r in all_resources:
            if r.slug:
                by_slug[r.slug] = r
        print(f"\nTotal resources in DB: {len(all_resources)}")
        print(f"Resources with slugs: {len(by_slug)}")

        # Build the set of replacement-required resource slugs
        replacement_slugs = set()
        for item in REPAIR_QUEUE.get("RESOURCE_REPLACEMENT_REQUIRED", []):
            replacement_slugs.add(item["resource"])
        print(f"Replacement-required slugs (the 66): {len(replacement_slugs)}")

        # ============================================================
        # PHASE B: Boundary-only fixes (46)
        # ============================================================
        print("\n" + "=" * 70)
        print("PHASE B: Apply boundary-only fixes")
        print("=" * 70)
        boundary_fixes = REPAIR_QUEUE.get("BOUNDARY_ONLY_FIX", [])
        boundary_fixed = 0
        boundary_details = []

        for item in boundary_fixes:
            slug = item["resource"]
            r = by_slug.get(slug)
            if not r:
                msg = f"  WARN: Resource {slug} not found in DB"
                print(msg)
                boundary_details.append({"slug": slug, "action": "NOT_FOUND"})
                continue

            issue = item.get("issue", "")
            old = {
                "boundary_type": r.boundary_type,
                "start_boundary": r.start_boundary,
                "end_boundary": r.end_boundary,
                "section": r.section,
                "exactness": r.exactness,
            }

            if "FULL_PAGE_STILL_VALID" in issue:
                # Full page covers the objective — promote to full-page
                r.boundary_type = "FULL_SINGLE_PAGE"
                r.start_boundary = None
                r.end_boundary = None
                r.section = None
                r.exactness = "FULL_SINGLE_PAGE"
                action = "FULL_PAGE_FIX"
            else:
                # BOUNDARY_RENAMED — section heading changed, can't verify new
                # heading name without fetching, so promote to full page
                r.boundary_type = "FULL_SINGLE_PAGE"
                r.start_boundary = None
                r.end_boundary = None
                r.section = None
                r.exactness = "FULL_SINGLE_PAGE"
                action = "BOUNDARY_RENAMED_FIX"

            boundary_fixed += 1
            boundary_details.append({
                "slug": slug,
                "action": action,
                "old": old,
            })
            print(f"  [OK] {slug}: {action}")

        db.flush()
        print(f"\nBoundary fixes applied: {boundary_fixed}/{len(boundary_fixes)}")

        # ============================================================
        # PHASE C: Canonical URL fixes (134)
        # ============================================================
        print("\n" + "=" * 70)
        print("PHASE C: Apply canonical URL fixes")
        print("=" * 70)
        canonical_fixes = REPAIR_QUEUE.get("CANONICAL_URL_FIX", [])
        canonical_fixed = 0
        canonical_skipped = 0
        canonical_already = 0
        canonical_details = []

        for item in canonical_fixes:
            slug = item["resource"]
            r = by_slug.get(slug)
            if not r:
                print(f"  WARN: Resource {slug} not found in DB")
                canonical_details.append({"slug": slug, "action": "NOT_FOUND"})
                continue

            old_url = item["old_url"]
            new_url = item["final_url"]

            # Already at canonical?
            if r.url == new_url:
                canonical_already += 1
                canonical_details.append({
                    "slug": slug,
                    "action": "ALREADY_CANONICAL",
                })
                continue

            # URL mismatch with expected old_url — the DB may have been
            # partially updated.  Only proceed if the DB still has the old URL.
            if r.url != old_url:
                print(f"  WARN {slug}: stored URL != expected old_url")
                print(f"       stored:   {r.url[:80]}")
                print(f"       expected: {old_url[:80]}")
                # Still apply — the new canonical is authoritative
                canonical_details.append({
                    "slug": slug,
                    "action": "URL_UPDATED_MISMATCH_WARN",
                    "stored_url": r.url,
                    "old_url": old_url,
                    "new_url": new_url,
                })
            else:
                canonical_details.append({
                    "slug": slug,
                    "action": "URL_UPDATED",
                    "old_url": old_url,
                    "new_url": new_url,
                })

            r.url = new_url
            canonical_fixed += 1
            print(f"  [OK] {slug}")

        db.flush()
        print(f"\nCanonical URL fixes applied: {canonical_fixed}")
        print(f"Already at canonical: {canonical_already}")
        print(f"Total processed: {canonical_fixed + canonical_already}/{len(canonical_fixes)}")

        # ============================================================
        # PHASE D: Provider metadata fixes (3)
        # ============================================================
        print("\n" + "=" * 70)
        print("PHASE D: Apply provider metadata fixes")
        print("=" * 70)
        metadata_fixes = REPAIR_QUEUE.get("METADATA_FIX", [])
        metadata_fixed = 0
        metadata_details = []

        for item in metadata_fixes:
            slug = item["resource"]
            r = by_slug.get(slug)
            if not r:
                print(f"  WARN: Resource {slug} not found in DB")
                metadata_details.append({"slug": slug, "action": "NOT_FOUND"})
                continue

            old_provider = r.provider
            old_title = r.title

            # Fix provider
            r.provider = "CS231n"

            # Fix title — use curated title if available, else patch
            if slug in TITLE_CORRECTIONS:
                r.title = TITLE_CORRECTIONS[slug]
            elif old_title and "PyTorch" in old_title:
                r.title = old_title.replace("PyTorch", "CS231n")

            metadata_fixed += 1
            metadata_details.append({
                "slug": slug,
                "action": "PROVIDER_FIXED",
                "old_provider": old_provider,
                "new_provider": "CS231n",
                "old_title": old_title,
                "new_title": r.title,
            })
            print(f"  [OK] {slug}: {old_provider!r} -> 'CS231n'")
            print(f"    title: {old_title!r} -> {r.title!r}")

        db.flush()
        print(f"\nProvider metadata fixes applied: {metadata_fixed}/{len(metadata_fixes)}")

        # ============================================================
        # PHASE E: Verify learner data unchanged
        # ============================================================
        print("\n" + "=" * 70)
        print("PHASE E: Verify learner data unchanged")
        print("=" * 70)
        after = snapshot_learner_data(db)

        all_match = True
        for key in before:
            status = "[OK]" if before[key] == after[key] else "[FAIL]"
            if before[key] != after[key]:
                all_match = False
            print(f"  {status} {key}: {before[key]} -> {after[key]}")

        if not all_match:
            print("\n!!! LEARNER DATA MUTATION DETECTED — ROLLING BACK !!!")
            db.rollback()
            sys.exit(1)

        # ============================================================
        # COMMIT
        # ============================================================
        db.commit()
        print("\n[OK] All changes committed. Learner data verified unchanged.")

        # ============================================================
        # PHASE F: Post-commit duplicate check
        # ============================================================
        print("\n" + "=" * 70)
        print("PHASE F: Post-commit duplicate check")
        print("=" * 70)
        from app.content.learner_visibility import is_learner_visible

        fresh_resources = db.query(CurriculumResource).all()
        visible = [r for r in fresh_resources if is_learner_visible(r)]
        url_lesson_pairs = {}
        duplicates = []
        for r in visible:
            key = (r.url, r.lesson_id)
            if key in url_lesson_pairs:
                duplicates.append({
                    "slug_a": url_lesson_pairs[key],
                    "slug_b": r.slug,
                    "url": r.url,
                    "lesson_id": r.lesson_id,
                })
            else:
                url_lesson_pairs[key] = r.slug

        if duplicates:
            print(f"  [WARN] Found {len(duplicates)} duplicate URL-lesson pairs:")
            for d in duplicates[:10]:
                print(f"    {d['slug_a']} ↔ {d['slug_b']}: {d['url'][:80]}")
        else:
            print("  [OK] No duplicate URL-lesson pairs found")

        # ============================================================
        # Summary report
        # ============================================================
        print("\n" + "=" * 70)
        print("MECHANICAL REPAIR SUMMARY")
        print("=" * 70)
        summary = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "boundary_fixes": {
                "applied": boundary_fixed,
                "total_in_queue": len(boundary_fixes),
            },
            "canonical_url_fixes": {
                "applied": canonical_fixed,
                "already_canonical": canonical_already,
                "total_in_queue": len(canonical_fixes),
            },
            "metadata_fixes": {
                "applied": metadata_fixed,
                "total_in_queue": len(metadata_fixes),
            },
            "learner_data_before": before,
            "learner_data_after": after,
            "learner_data_match": all_match,
            "duplicate_check": {
                "duplicates_found": len(duplicates),
                "details": duplicates,
            },
            "details": {
                "boundary": boundary_details,
                "canonical": canonical_details,
                "metadata": metadata_details,
            },
        }

        out = REPORT_DIR / "mechanical_repair_summary.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        print(f"\nBoundary fixes:      {boundary_fixed}/{len(boundary_fixes)}")
        print(f"Canonical URL fixes: {canonical_fixed}/{len(canonical_fixes)}")
        print(f"Provider fixes:      {metadata_fixed}/{len(metadata_fixes)}")
        print(f"Learner data:        {'[OK] UNCHANGED' if all_match else '[FAIL] MUTATED'}")
        print(f"Duplicates:          {len(duplicates)}")
        print(f"\nFull report: {out}")

    except Exception as e:
        db.rollback()
        print(f"\n!!! ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
