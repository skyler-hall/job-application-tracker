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
