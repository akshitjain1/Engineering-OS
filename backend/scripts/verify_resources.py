"""INDEPENDENT RESOURCE VERIFIER"""
import json, hashlib, re, urllib.request, urllib.error, urllib.parse, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, r"D:\Akshit Personal OS\backend")
from app.db.session import SessionLocal
from app.db.models import CurriculumResource, CurriculumLesson
from app.content.learner_visibility import is_learner_visible

REPORT_DIR = Path(r"D:\Akshit Personal OS\backend\reports")
YOUTUBE_API_KEY = __import__("os").getenv("YOUTUBE_API_KEY")

def fetch_url(url, timeout=15):
    headers = {"User-Agent": "Mozilla/5.0 (EngineeringOS-Verifier/1.0)"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.url, resp.read(500000), resp.headers.get("Content-Type",""), None
    except urllib.error.HTTPError as e:
        return e.code, url, b"", "", str(e)
    except Exception as e:
        return 0, url, b"", "", str(e)

def extract_headings(html_text):
    headings = re.findall(r"<h[1-6][^>]*>(.*?)</h[1-6]>", html_text, re.IGNORECASE|re.DOTALL)
    cleaned=[]
    for h in headings[:20]:
        h=re.sub(r"<[^>]+>","",h).strip()
        if h: cleaned.append(h[:150])
    return cleaned

def youtube_video_id(url):
    if not url: return None
    m=re.search(r"(?:v=|youtu\.be/|embed/)([^&\n?#]+)", url)
    return m.group(1) if m else None

def is_youtube_playlist(url, resource_type=None):
    if (resource_type or "")=="youtube_playlist": return True
    if not url: return False
    if youtube_video_id(url): return False
    return "playlist" in url.lower() or "list=" in url.lower()

def main():
    db=SessionLocal()
    try:
        lessons=db.query(CurriculumLesson).all()
        lesson_topic={l.id: l.topic_id for l in lessons}
        resources=db.query(CurriculumResource).all()
        targets=[r for r in resources if is_learner_visible(r) and (r.role or "").upper() in ("PRIMARY","PRIMARY_LEARN")]
        print(f"Checking {len(targets)} learner-visible PRIMARY resources")
        distinct_urls=set(r.url for r in targets if r.url)
        print(f"Distinct URLs: {len(distinct_urls)}")
        evidence=[]
        failures={"DEAD":[],"MOVED":[],"UNREACHABLE":[],"PLAYLIST_ONLY":[],"MISSING_VIDEO_ID":[],"SECTION_NOT_FOUND":[],"NEEDS_REVIEW":[],"PROVIDER_MISMATCH":[]}
        passed=0
        for r in targets:
            rec={"resource_id":r.id,"slug":r.slug,"title":r.title,"url":r.url,"provider":r.provider,"resource_type":r.resource_type,"role":r.role,"exactness":r.exactness,"boundary_type":getattr(r,"boundary_type",None),"start_boundary":getattr(r,"start_boundary",None) or getattr(r,"section",None),"end_boundary":getattr(r,"end_boundary",None) or getattr(r,"lecture",None),"video_id":getattr(r,"video_id",None),"estimated_minutes":r.estimated_minutes,"verification_status":r.verification_status}
            if is_youtube_playlist(r.url, r.resource_type) and not getattr(r,"video_id",None):
                rec["failure"]="PLAYLIST_ONLY"
                failures["PLAYLIST_ONLY"].append(rec)
                evidence.append(rec)
                continue
            url_lower=(r.url or "").lower()
            provider_lower=(r.provider or "").lower()
            mismatch=False
            if "pytorch" in url_lower and "pytorch" not in provider_lower: mismatch=True
            elif "cs231n" in url_lower and "cs231n" not in provider_lower and "stanford" not in provider_lower: mismatch=True
            elif "d2l.ai" in url_lower and "d2l" not in provider_lower and "dive" not in provider_lower: mismatch=True
            elif "huggingface" in url_lower and "hugging" not in provider_lower: mismatch=True
            if mismatch:
                rec["provider_mismatch"]=True
                failures["PROVIDER_MISMATCH"].append(rec)
            status, final_url, body, ctype, err=fetch_url(r.url)
            rec["http_status"]=status
            rec["final_url"]=final_url
            rec["content_hash"]=hashlib.sha256(body).hexdigest()[:16] if body else None
            rec["content_length"]=len(body)
            if status==0:
                rec["failure"]="UNREACHABLE"
                failures["UNREACHABLE"].append(rec)
            elif status>=400:
                rec["failure"]="DEAD"
                failures["DEAD"].append(rec)
            elif final_url!=r.url:
                rec["moved"]=True
                failures["MOVED"].append(rec)
            if body and b"<html" in body.lower()[:1000]:
                try:
                    html_text=body.decode("utf-8",errors="ignore")
                    m=re.search(r"<title[^>]*>(.*?)</title>",html_text,re.IGNORECASE|re.DOTALL)
                    rec["page_title"]=re.sub(r"<[^>]+>","",m.group(1)).strip()[:150] if m else None
                    rec["headings"]=extract_headings(html_text)
                    bt=getattr(r,"boundary_type",None)
                    sb=getattr(r,"start_boundary",None) or getattr(r,"section",None)
                    if bt in ("ARTICLE_SECTION","BOOK_SECTION") and sb and sb!="FULL_SINGLE_PAGE":
                        if not any(sb.lower() in h.lower() for h in rec["headings"]) and sb.lower() not in html_text.lower():
                            rec["section_not_found"]=sb
                            rec["failure"]="SECTION_NOT_FOUND"
                            failures["SECTION_NOT_FOUND"].append(rec)
                except Exception as e:
                    rec["parse_error"]=str(e)
            vid=youtube_video_id(r.url) or getattr(r,"video_id",None)
            rec["youtube_video_id"]=vid
            if r.resource_type=="youtube" or "youtube" in url_lower or "youtu.be" in url_lower:
                if not vid:
                    rec["failure"]="MISSING_VIDEO_ID"
                    failures["MISSING_VIDEO_ID"].append(rec)
                else:
                    rec["youtube_url"]=f"https://www.youtube.com/watch?v={vid}"
                    if not YOUTUBE_API_KEY:
                        rec["youtube_needs_review"]=True
            if not rec.get("failure"):
                if rec.get("section_not_found"):
                    failures["SECTION_NOT_FOUND"].append(rec)
                else:
                    passed+=1
            evidence.append(rec)
        failed=sum(len(v) for k,v in failures.items() if k not in ("PROVIDER_MISMATCH","MOVED"))
        print(f"Checked: {len(targets)}, Passed: {passed}, Failed: {failed}")
        for k,v in failures.items():
            if v: print(f"  {k}: {len(v)}")
        print(f"  MOVED: {len([r for r in evidence if r.get('moved')])}")
        from collections import Counter
        url_counts=Counter(r.url for r in targets if r.url)
        print(f"Most reused URLs: {url_counts.most_common(3)}")
        print(f"False previously verified: {len([r for r in evidence if r.get('failure') and (r.get('verification_status') or '').upper() in ('VERIFIED','VERIFIED_COVERAGE')])}")
        with open(REPORT_DIR / "resource_verification_evidence.json","w",encoding="utf-8") as f:
            json.dump({"generated_at": datetime.now(timezone.utc).isoformat(),"evidence":evidence},f,indent=2)
        with open(REPORT_DIR / "resource_verification_failures.json","w",encoding="utf-8") as f:
            json.dump(failures,f,indent=2)
        md=f"# Resource Verification Report\n\nGenerated: {datetime.now(timezone.utc).isoformat()}\n\n## Summary\n- Checked: {len(targets)}\n- Distinct URLs: {len(distinct_urls)}\n- Passed: {passed}\n- Failed: {failed}\n\n## Failures by Category\n"
        for k,v in failures.items():
            md+=f"- {k}: {len(v)}\n"
        for cat,items in failures.items():
            if items:
                md+=f"\n## {cat} ({len(items)})\n"
                for it in items[:10]:
                    md+=f"- {it['slug']}: {it['url']} - {it.get('detail','')}\n"
        (REPORT_DIR / "resource_verification_report.md").write_text(md,encoding="utf-8")
        print("Reports written")
        return 0
    finally:
        db.close()

if __name__=="__main__":
    import sys
    sys.exit(main())
