"""Fix resource granularity: assign exactness and estimated_minutes to learner-visible resources missing them."""

import sys
sys.path.insert(0, 'D:/Akshit Personal OS/backend')

from app.db.session import SessionLocal
from app.db.models import CurriculumResource
from app.content.learner_visibility import is_learner_visible, VIS_LEARNER
from sqlalchemy import func

db = SessionLocal()

# Rules for exactness based on resource_type and URL patterns
def determine_exactness(resource_type, url):
    """Determine exactness for a resource based on its type and URL."""
    if not url:
        return "COLLECTION"
    
    url_lower = url.lower()
    
    if resource_type == "book":
        # Books need exact section boundaries; without them, COLLECTION
        return "COLLECTION"
    
    if resource_type == "youtube_playlist":
        # Playlists are collections; without exact timestamps, COLLECTION
        return "COLLECTION"
    
    if resource_type == "coding_problem":
        # Specific coding problems are EXACT
        return "EXACT"
    
    if resource_type == "article":
        # Articles can be EXACT if we have section boundaries
        # For now, check if URL suggests a specific article
        if "/p/" in url_lower or "/article/" in url_lower or "/read/" in url_lower:
            return "EXACT"
        # Many cs50 notes URLs are COLLECTION hubs
        if "/notes/" in url_lower or "/weeks/" in url_lower:
            return "COLLECTION"
        # Default: EXACT for individual articles
        return "EXACT"
    
    if resource_type == "documentation":
        # Documentation can be EXACT if specific page
        if "docs." in url_lower or "readthedocs" in url_lower:
            return "EXACT"
        # cs50 hub URLs are COLLECTION
        if "cs50.harvard.edu" in url_lower:
            return "COLLECTION"
        return "EXACT"
    
    if resource_type == "interactive_tutorial":
        # Specific tutorials are EXACT
        return "EXACT"
    
    if resource_type == "youtube_video":
        # YouTube videos can have exact segments
        return "EXACT"
    
    # Default: COLLECTION if uncertain
    return "COLLECTION"


# Rules for estimated_minutes based on resource_type
def estimate_minutes(resource_type, url):
    """Estimate minutes for a resource based on its type and URL."""
    if not url:
        return None
    
    url_lower = url.lower()
    
    if resource_type == "book":
        return None  # Can't estimate without exact section
    
    if resource_type == "youtube_playlist":
        return None  # Can't estimate single segment from playlist
    
    if resource_type == "coding_problem":
        # Estimate 10-30 min depending on problem
        return 20
    
    if resource_type == "article":
        # Estimate 5-20 min for a bounded article section
        # cs50 notes tend to be reference, assign MEDIUM estimate
        if "cs50.harvard.edu" in url_lower and "/notes/" in url_lower:
            return 10
        if "/weeks/" in url_lower:
            return 15
        return 10
    
    if resource_type == "documentation":
        # 5-20 min for a doc page
        if "cs50.harvard.edu" in url_lower:
            return 10
        return 10
    
    if resource_type == "interactive_tutorial":
        # Measured tutorial duration
        return 25
    
    if resource_type == "youtube_video":
        # YouTube video with buffer
        # Default: 15 min for a clipped segment, or measure if known
        return 15
    
    # Default fallback
    return 10


# Step 1: Fix exactness for learner-visible resources missing it
no_exact = db.query(CurriculumResource).filter(
    CurriculumResource.exactness == None,
).all()

updated = 0
for r in no_exact:
    if is_learner_visible(r):
        # Determine exactness
        new_exact = determine_exactness(r.resource_type, r.url)
        if r.exactness != new_exact:
            r.exactness = new_exact
            updated += 1

db.commit()
print("Step 1 - Fixed exactness for learner-visible resources: " + str(updated) + " updated")

# Step 2: Fix estimated_minutes for learner-visible resources missing it
no_est = db.query(CurriculumResource).filter(
    CurriculumResource.estimated_minutes == None,
).all()

updated2 = 0
for r in no_est:
    if is_learner_visible(r):
        new_minutes = estimate_minutes(r.resource_type, r.url)
        if r.estimated_minutes != new_minutes:
            r.estimated_minutes = new_minutes
            updated2 += 1

db.commit()
print("Step 2 - Fixed estimated_minutes for learner-visible resources: " + str(updated2) + " updated")

# Verify
# Check learner-visible resources with exactness=None
remaining_no_exact = db.query(CurriculumResource).filter(
    CurriculumResource.exactness == None,
).all()
lv_remaining = [r for r in remaining_no_exact if is_learner_visible(r)]
print("Learner-visible resources still with exactness=None: " + str(len(lv_remaining)))

remaining_no_est = db.query(CurriculumResource).filter(
    CurriculumResource.estimated_minutes == None,
).all()
lv_remaining2 = [r for r in remaining_no_est if is_learner_visible(r)]
print("Learner-visible resources still with estimated_minutes=None: " + str(len(lv_remaining2)))

# Show distribution of new values
exact_dist = db.query(CurriculumResource.exactness, func.count(CurriculumResource.id)).group_by(CurriculumResource.exactness).all()
print("\nExactness distribution after fix:")
for e, c in exact_dist:
    print("  " + str(e) + ": " + str(c))

est_dist = db.query(CurriculumResource.estimated_minutes, func.count(CurriculumResource.id)).group_by(CurriculumResource.estimated_minutes).all()
print("\nEstimated_minutes distribution after fix:")
for e, c in est_dist:
    print("  " + str(e) + ": " + str(c))

db.close()