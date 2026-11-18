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