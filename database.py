"""Database connection and query helpers for the Job Application Tracker."""
import os

import mysql.connector
from dotenv import load_dotenv

# Read DB_HOST, DB_USER, DB_PASSWORD, DB_NAME from the .env file
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "job_tracker"),
}


def get_db():
    """Open a new connection to the MySQL database."""
    return mysql.connector.connect(**DB_CONFIG)


def query_all(sql, params=None):
    """Run a SELECT and return every row as a list of dictionaries."""
    conn = get_db()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        return cursor.fetchall()
    finally:
        conn.close()


def query_one(sql, params=None):
    """Run a SELECT and return just the first row (or None)."""
    rows = query_all(sql, params)
    return rows[0] if rows else None


def execute(sql, params=None):
    """Run an INSERT, UPDATE, or DELETE and save the change.
    Returns the new row's id for INSERTs."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


# ---------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------

STATUSES = ["Applied", "Screening", "Interview", "Offer", "Rejected", "Withdrawn"]


def get_dashboard_stats():
    """Collect everything the dashboard page needs in one dictionary."""
    counts = query_one("""
        SELECT (SELECT COUNT(*) FROM companies)    AS companies,
               (SELECT COUNT(*) FROM jobs)         AS jobs,
               (SELECT COUNT(*) FROM applications) AS applications,
               (SELECT COUNT(*) FROM contacts)     AS contacts,
               (SELECT COUNT(*) FROM events)       AS events
    """)

    # How many applications are in each status (0 if none)
    rows = query_all("SELECT status, COUNT(*) AS total FROM applications GROUP BY status")
    by_status = {status: 0 for status in STATUSES}
    for row in rows:
        by_status[row["status"]] = row["total"]

    # Response rate = applications that got past "Applied", ignoring withdrawn ones
    active = counts["applications"] - by_status["Withdrawn"]
    responded = active - by_status["Applied"]
    response_rate = round(responded / active * 100) if active else 0

    recent = query_all("""
        SELECT a.application_id, a.application_date, a.status,
               j.job_title, c.company_name
        FROM applications a
        JOIN jobs j      ON a.job_id = j.job_id
        JOIN companies c ON j.company_id = c.company_id
        ORDER BY a.application_date DESC
        LIMIT 5
    """)

    upcoming_events = query_all("""
        SELECT e.event_id, e.event_name, e.event_type, e.event_date, c.company_name
        FROM events e
        LEFT JOIN companies c ON e.company_id = c.company_id
        WHERE e.event_date >= CURDATE()
        ORDER BY e.event_date
        LIMIT 5
    """)

    return {
        "counts": counts,
        "by_status": by_status,
        "response_rate": response_rate,
        "recent": recent,
        "upcoming_events": upcoming_events,
    }

# ---------------------------------------------------------------------
# Companies
# ---------------------------------------------------------------------

def get_companies(search=None):
    """All companies (optionally filtered by a search term), with how many
    jobs and contacts each one has."""
    sql = """
        SELECT c.*,
               (SELECT COUNT(*) FROM jobs j     WHERE j.company_id = c.company_id)  AS job_count,
               (SELECT COUNT(*) FROM contacts t WHERE t.company_id = c.company_id) AS contact_count
        FROM companies c
    """
    params = []
    if search:
        sql += " WHERE c.company_name LIKE %s OR c.industry LIKE %s OR c.city LIKE %s"
        like = f"%{search}%"
        params = [like, like, like]
    sql += " ORDER BY c.company_name"
    return query_all(sql, params)


def get_company(company_id):
    return query_one("SELECT * FROM companies WHERE company_id = %s", (company_id,))


def create_company(data):
    return execute("""
        INSERT INTO companies (company_name, industry, website, city, state, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (data["company_name"], data["industry"], data["website"],
          data["city"], data["state"], data["notes"]))


def update_company(company_id, data):
    execute("""
        UPDATE companies
        SET company_name = %s, industry = %s, website = %s,
            city = %s, state = %s, notes = %s
        WHERE company_id = %s
    """, (data["company_name"], data["industry"], data["website"],
          data["city"], data["state"], data["notes"], company_id))


def delete_company(company_id):
    execute("DELETE FROM companies WHERE company_id = %s", (company_id,))


def get_company_related(company_id):
    """Jobs, contacts, and events linked to one company (for its detail page)."""
    return {
        "jobs": query_all(
            "SELECT * FROM jobs WHERE company_id = %s ORDER BY date_posted DESC",
            (company_id,)),
        "contacts": query_all(
            "SELECT * FROM contacts WHERE company_id = %s ORDER BY contact_name",
            (company_id,)),
        "events": query_all(
            "SELECT * FROM events WHERE company_id = %s ORDER BY event_date DESC",
            (company_id,)),
    }