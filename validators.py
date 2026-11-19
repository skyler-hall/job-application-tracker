"""Form validation helpers. Each validate_* function takes request.form and
returns (data, errors): a clean dictionary ready for the database, and a
list of error messages to show the user (empty if everything is valid)."""
import re
from datetime import date

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def clean(value):
    """Trim whitespace and turn empty strings into None (NULL in MySQL)."""
    if value is None:
        return None
    value = value.strip()
    return value or None


def check_length(errors, label, value, max_len):
    if value and len(value) > max_len:
        errors.append(f"{label} must be {max_len} characters or fewer.")


def check_url(errors, label, value):
    if value and not value.startswith(("http://", "https://")):
        errors.append(f"{label} must start with http:// or https://")


def check_date(errors, label, value, required=False):
    """Make sure a date string is a real YYYY-MM-DD date."""
    if not value:
        if required:
            errors.append(f"{label} is required.")
        return
    try:
        date.fromisoformat(value)
    except ValueError:
        errors.append(f"{label} must be a valid date.")


def validate_company(form):
    errors = []
    data = {
        "company_name": clean(form.get("company_name")),
        "industry": clean(form.get("industry")),
        "website": clean(form.get("website")),
        "city": clean(form.get("city")),
        "state": clean(form.get("state")),
        "notes": clean(form.get("notes")),
    }
    if not data["company_name"]:
        errors.append("Company name is required.")
    check_length(errors, "Company name", data["company_name"], 100)
    check_length(errors, "Industry", data["industry"], 50)
    check_length(errors, "Website", data["website"], 200)
    check_length(errors, "City", data["city"], 50)
    check_length(errors, "State", data["state"], 50)
    check_url(errors, "Website", data["website"])
    return data, errors

JOB_TYPES = ["Full-time", "Part-time", "Contract", "Internship"]


def parse_skills(text):
    """Turn "Python, SQL,  flask" into ["Python", "SQL", "flask"], skipping
    blanks and duplicates (case-insensitive)."""
    skills, seen = [], set()
    for part in (text or "").split(","):
        skill = part.strip()
        if skill and skill.lower() not in seen:
            seen.add(skill.lower())
            skills.append(skill)
    return skills


def parse_int(errors, label, value):
    """Convert a form value to a whole number, or None if empty."""
    if not value:
        return None
    try:
        number = int(value.replace(",", ""))
    except ValueError:
        errors.append(f"{label} must be a whole number.")
        return None
    if number < 0:
        errors.append(f"{label} cannot be negative.")
    return number


def validate_job(form, company_ids):
    errors = []
    data = {
        "company_id": clean(form.get("company_id")),
        "job_title": clean(form.get("job_title")),
        "job_type": clean(form.get("job_type")),
        "job_url": clean(form.get("job_url")),
        "date_posted": clean(form.get("date_posted")),
        "skills": parse_skills(form.get("requirements")),
    }
    data["salary_min"] = parse_int(errors, "Minimum salary", clean(form.get("salary_min")))
    data["salary_max"] = parse_int(errors, "Maximum salary", clean(form.get("salary_max")))

    if not data["company_id"] or not data["company_id"].isdigit() or int(data["company_id"]) not in company_ids:
        errors.append("Please choose a company.")
    if not data["job_title"]:
        errors.append("Job title is required.")
    check_length(errors, "Job title", data["job_title"], 100)
    if data["job_type"] and data["job_type"] not in JOB_TYPES:
        errors.append("Please choose a valid job type.")
    check_length(errors, "Job URL", data["job_url"], 300)
    check_url(errors, "Job URL", data["job_url"])
    check_date(errors, "Date posted", data["date_posted"])
    if (data["salary_min"] is not None and data["salary_max"] is not None
            and data["salary_min"] > data["salary_max"]):
        errors.append("Minimum salary cannot be more than maximum salary.")
    return data, errors

def validate_contact(form, company_ids):
    errors = []
    data = {
        "company_id": clean(form.get("company_id")),
        "contact_name": clean(form.get("contact_name")),
        "title": clean(form.get("title")),
        "email": clean(form.get("email")),
        "phone": clean(form.get("phone")),
        "linkedin_url": clean(form.get("linkedin_url")),
        "notes": clean(form.get("notes")),
    }
    if not data["company_id"] or not data["company_id"].isdigit() or int(data["company_id"]) not in company_ids:
        errors.append("Please choose a company.")
    if not data["contact_name"]:
        errors.append("Contact name is required.")
    check_length(errors, "Contact name", data["contact_name"], 100)
    check_length(errors, "Title", data["title"], 100)
    check_length(errors, "Email", data["email"], 100)
    check_length(errors, "Phone", data["phone"], 20)
    check_length(errors, "LinkedIn URL", data["linkedin_url"], 200)
    if data["email"] and not EMAIL_RE.match(data["email"]):
        errors.append("Email address doesn't look valid.")
    if data["phone"] and not re.fullmatch(r"[0-9+()\-.\s]{7,20}", data["phone"]):
        errors.append("Phone number can only contain digits, spaces, and + ( ) - .")
    check_url(errors, "LinkedIn URL", data["linkedin_url"])
    return data, errors

EVENT_TYPES = ["Career Fair", "Info Session", "Networking", "Workshop", "Conference", "Other"]


def validate_event(form, company_ids):
    errors = []
    data = {
        "company_id": clean(form.get("company_id")),
        "event_name": clean(form.get("event_name")),
        "event_type": clean(form.get("event_type")),
        "event_date": clean(form.get("event_date")),
        "location": clean(form.get("location")),
        "notes": clean(form.get("notes")),
    }
    # Company is optional for events (a career fair has many companies)
    if data["company_id"] and (not data["company_id"].isdigit() or int(data["company_id"]) not in company_ids):
        errors.append("Please choose a valid company.")
    if not data["event_name"]:
        errors.append("Event name is required.")
    check_length(errors, "Event name", data["event_name"], 100)
    if data["event_type"] and data["event_type"] not in EVENT_TYPES:
        errors.append("Please choose a valid event type.")
    check_date(errors, "Event date", data["event_date"], required=True)
    check_length(errors, "Location", data["location"], 100)
    return data, errors