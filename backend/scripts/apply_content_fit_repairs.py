from app.content.apply_content_fit_repairs import apply_content_fit_repairs
from app.db.session import SessionLocal


if __name__ == "__main__":
    db = SessionLocal()
    try:
        import json
        print(json.dumps(apply_content_fit_repairs(db), indent=2))
    finally:
        db.close()
