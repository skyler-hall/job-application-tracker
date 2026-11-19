"""Job Match: compare the user's skills to each job's required skills
(stored as a JSON list in jobs.requirements) and rank jobs by match %."""
from collections import Counter

# Common nicknames so "JS" matches "JavaScript", etc.
ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "golang": "go",
    "postgres": "postgresql",
    "k8s": "kubernetes",
    "ml": "machine learning",
    "c plus plus": "c++",
    "cpp": "c++",
}


def normalize(skill):
    """Lowercase, trim, squeeze extra spaces, and apply aliases."""
    key = " ".join(skill.lower().split())
    return ALIASES.get(key, key)


def parse_skill_input(text):
    """Split the user's comma-separated skills, dropping blanks and duplicates."""
    skills, seen = [], set()
    for part in (text or "").split(","):
        skill = part.strip()
        if skill and normalize(skill) not in seen:
            seen.add(normalize(skill))
            skills.append(skill)
    return skills


def calculate_match(user_skills, job_skills):
    """Return (percent, matched, missing) for one job.

    percent = matched required skills / total required skills * 100
    Example: user has Python, SQL, Flask; job needs Python, SQL, Tableau
             -> 67%, matched [Python, SQL], missing [Tableau]
    """
    if not job_skills:
        return 0, [], []
    user_set = {normalize(s) for s in user_skills}
    matched = [s for s in job_skills if normalize(s) in user_set]
    missing = [s for s in job_skills if normalize(s) not in user_set]
    percent = round(len(matched) / len(job_skills) * 100)
    return percent, matched, missing


def rank_jobs(user_skills, jobs, include_zero=False):
    """Score every job and sort best match first.

    jobs: list of dicts that each have a 'skills' list.
    Returns (results, skills_to_learn) where skills_to_learn is the
    missing skills that show up most often across the matched jobs.
    """
    results = []
    for job in jobs:
        if not job.get("skills"):
            continue  # can't score a job with no listed requirements
        percent, matched, missing = calculate_match(user_skills, job["skills"])
        if percent == 0 and not include_zero:
            continue
        results.append({**job, "percent": percent, "matched": matched, "missing": missing})

    # Highest % first; ties go to the job where you match more skills
    results.sort(key=lambda r: (-r["percent"], -len(r["matched"]), r["job_title"]))

    missing_counts = Counter(skill for r in results for skill in r["missing"])
    skills_to_learn = missing_counts.most_common(5)
    return results, skills_to_learn