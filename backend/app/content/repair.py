"""Idempotent curriculum data repairs, on demand instead of on every boot.

These used to run at import time in app.main, which meant every server start,
every test session and every one-off `python -c` paid for a full curriculum
rewrite. They are idempotent and the data they fix changes only when content
changes, so they belong behind a command.

Run manually:      python -m app.content.repair
Run on boot:       set EOS_RUN_REPAIRS=1
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def run_all(db: Session) -> None:
    """Every repair, in the order app.main used to run them.

    Order matters: the verification-status restore has to come after the
    content repairs, and the learner-visibility pass has to come last so it
    hides internal resources the earlier steps may have (re)created.
    """
    from app.content.backfill_tracks import backfill_topic_tracks
    from app.content.domain0_repair import apply_domain0_repairs
    from app.content.dsa_practice import enrich_dsa_practice
    from app.content.learner_visibility import (
        apply_learner_visibility,
        restore_content_verification_statuses,
    )
    from app.learning.projects import seed_projects

    backfill_topic_tracks(db)
    apply_domain0_repairs(db)
    enrich_dsa_practice(db)
    seed_projects(db)
    # After repairs: restore content-verification statuses, then hide internal resources.
    restore_content_verification_statuses(db)
    apply_learner_visibility(db)


def main() -> None:
    with SessionLocal() as db:
        run_all(db)
        db.commit()
    print("repairs complete")


if __name__ == "__main__":
    main()
