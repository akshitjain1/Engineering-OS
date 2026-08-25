"""Complete learner contract repair script."""
import sys
sys.path.insert(0, r"D:\Akshit Personal OS\backend")

from app.db.session import SessionLocal
from app.db.models import CurriculumTopic, CurriculumResource, CurriculumLesson, LessonExercise
from app.content.learner_visibility import is_learner_visible
import re

REPORT_DIR = r"D:\Akshit Personal OS\backend\reports"

def main():
    db = SessionLocal()
    try:
        # 1. Add estimated_minutes to all topics missing it
        topics = db.query(CurriculumTopic).all()
        updated = 0
        for t in topics:
            if not t.estimated_minutes:
                t.estimated_minutes = 30
        print(f"Updated estimated_minutes for topics")

        # Fix resource boundaries
        from app.content.learner_visibility import is_learner_visible
        resources = db.query(CurriculumResource).all()
        boundary_fixed = 0
        for r in resources:
            if r.learner_visible and (r.role or "").upper() in ("PRIMARY", "PRIMARY_LEARN"):
                rt = (r.resource_type or "").lower()
                if "youtube" in r.url.lower() or "video" in rt:
                    if not r.video_id:
                        m = re.search(r"(?:v=|youtu\.be/|embed/)([^&\n?]+)", r.url or "")
                        if m:
                            r.video_id = m.group(1)
                    if r.estimated_minutes is None or r.estimated_minutes == 0:
                        r.estimated_minutes = 20
                elif "article" in r.resource_type.lower() or "documentation" in rt:
                    if not r.section and not r.lecture:
                        if r.description:
                            m = re.search(r"section[:\s]+([^.]+)", r.description, re.IGNORECASE)
                            if m:
                                r.section = m.group(1).strip()
                    if r.estimated_minutes is None or r.estimated_minutes == 0:
                        r.estimated_minutes = 25
                elif "book" in rt:
                    if not r.section:
                        m = re.search(r"chapter\s+(\d+)", r.description or "", re.IGNORECASE)
                        if m:
                            r.section = f"Chapter {m.group(1)}"
                    if not r.lecture:
                        m = re.search(r"(section|chapter)\s+(\d+)", r.description or "", re.IGNORECASE)
                        if m:
                            r.lecture = f"Section {m.group(2)}"
        print("Fixed boundaries")

        # Fix practice contracts
        from app.db.models import LessonExercise
        exercises = db.query(LessonExercise).all()
        practice_fixed = 0
        for e in db.query(LessonExercise).all():
            if (not e.practice_instructions or e.practice_instructions.strip() == "") and e.quantity:
                e.practice_instructions = f"Complete {e.quantity} exercises on {e.topic or e.title}"
            if e.quantity is None and e.practice_instructions:
                e.quantity = 3
            if e.quantity is not None and e.quantity <= 0:
                e.quantity = 1
            if not e.objective and e.title:
                e.objective = e.title
            elif not e.objective:
                e.objective = e.title or "Complete practice"
        print("Fixed practice contracts")

        # Fix resource metadata
        meta_fixed = 0
        for r in db.query(CurriculumResource).all():
            if not r.provider and r.url:
                if "scikit-learn.org" in r.url:
                    r.provider = "scikit-learn"
                elif "pytorch.org" in r.url:
                    r.provider = "PyTorch"
                elif "docs.python.org" in r.url:
                    r.provider = "Python Software Foundation"
                elif "developer.mozilla.org" in r.url:
                    r.provider = "Mozilla"
                elif "geeksforgeeks.org" in r.url:
                    r.provider = "GeeksforGeeks"
                elif "d2l.ai" in r.url:
                    r.provider = "Dive into Deep Learning"
                elif "huggingface.co" in r.url:
                    r.provider = "Hugging Face"
                elif "anthropic.com" in r.url:
                    r.provider = "Anthropic"
                elif "platform.openai.com" in r.url:
                    r.provider = "OpenAI"
                elif "docs.cohere.com" in r.url:
                    r.provider = "Cohere"
                elif "docs.google.com" in r.url or "developers.google.com" in r.url:
                    r.provider = "Google"
                elif "opencv.org" in r.url:
                    r.provider = "OpenCV"
                elif "scikit-image.org" in r.url:
                    r.provider = "scikit-image"
                elif "mlflow.org" in r.url:
                    r.provider = "MLflow"
                elif "tutorial.math.lamar.edu" in r.url:
                    r.provider = "Paul's Online Math Notes"
            if meta_fixed > 0:
                meta_fixed += 1

        # Ensure provider matches URL for learner-visible PRIMARYs
        for r in db.query(CurriculumResource).filter(
            CurriculumResource.learner_visible == True,
            CurriculumResource.role.in_(["PRIMARY", "PRIMARY_LEARN"])
        ).all():
            if r.provider and r.url:
                prov_lower = r.provider.lower()
                if "scikit-learn" in r.url and "scikit" not in prov_lower:
                    r.provider = "scikit-learn"
                elif "pytorch" in r.url and "pytorch" not in prov_lower:
                    r.provider = "PyTorch"
                elif "d2l.ai" in r.url and "dive" not in prov_lower and "deep" not in prov_lower:
                    r.provider = "Dive into Deep Learning"
                elif "huggingface.co" in r.url and "hugging" not in prov_lower:
                    r.provider = "Hugging Face"
                elif "anthropic.com" in r.url and "anthropic" not in prov_lower:
                    r.provider = "Anthropic"
                elif "openai.com" in r.url and "openai" not in prov_lower:
                    r.provider = "OpenAI"
                elif "cohere.com" in r.url and "cohere" not in prov_lower:
                    r.provider = "Cohere"
                elif "mlflow.org" in r.url and "mlflow" not in prov_lower:
                    r.provider = "MLflow"

        # Ensure practice contracts exist
        practice_added = 0
        for t in db.query(CurriculumTopic).all():
            t_lessons = db.query(CurriculumLesson).filter(CurriculumLesson.topic_id == t.id).all()
            for lesson in t_lessons:
                existing = db.query(LessonExercise).filter(LessonExercise.lesson_id == lesson.id).first()
                if not existing:
                    ex = LessonExercise(
                        slug=f"{lesson.slug}-practice" if lesson.slug else f"ex-{lesson.id}",
                        title=f"Practice: {lesson.title}",
                        description=f"Practice exercises for {lesson.title}",
                        difficulty="beginner",
                        topic=lesson.title,
                        lesson_id=lesson.id,
                        exercise_type="SELF_REFLECTION",
                        destination_type="SELF_CHECK",
                        quantity=3,
                        concepts_required=[t.slug] if t.slug else [],
                        practice_instructions=(
                            f"1. Review the material for {lesson.title}.\n"
                            f"2. Complete 3 practice exercises related to the key concepts.\n"
                            f"3. Verify your understanding by explaining the main concept in your own words."
                        ),
                        completion_status="not_started",
                        evaluated=False,
                    )
                    db.add(ex)
                    practice_added += 1

        db.commit()
        print("All fixes applied successfully!")

    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()