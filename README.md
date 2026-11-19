# Job Application Tracker

A full-stack web app for tracking job applications, built with **MySQL**, **Python/Flask**, and **HTML/CSS**.
It keeps companies, job postings, applications (with interview rounds), recruiter contacts, and career events
in one place, and includes a **Job Match** feature that ranks jobs by how well your skills match their requirements.

Built for COP 4751 (Advanced Database Management), FIU, Fall 2026.

## Features

- **Dashboard:** totals for every table, response rate, applications by status, upcoming events, the
  companies you're currently interviewing with (and which round you're in), and recent applications.
- **Full CRUD** (create, read, update, delete) for **5 tables**: Companies, Jobs, Applications, Contacts, Events.
  - List pages with search and filters, detail pages, add/edit forms, and delete with a confirmation popup.
  - Server-side validation on every form (required fields, lengths, URLs, emails, phone numbers, dates,
    salary range, valid foreign keys), with friendly error messages.
- **JSON columns:**
  - `jobs.requirements` stores required skills, e.g. `["Python", "SQL", "Flask"]`
  - `applications.interview_data` stores each interview round (date, type, interviewer, notes)
- **Job Match:** enter your skills and see every job ranked by match %, with matched and missing skills
  and a "Skills to Learn Next" list.
- **Interview round tracking:** `applications.current_round` shows where you are in each process.

## Tech Stack

| Layer    | Technology |
|----------|------------|
| Database | MySQL 8 |
| Backend  | Python 3, Flask, mysql-connector-python, python-dotenv |
| Frontend | HTML (Jinja2 templates), CSS |

## Database Schema

| Table | Key columns | Relationships |
|-------|-------------|---------------|
| `companies` | company_id, company_name (unique), industry, website, city, state, notes | parent of jobs, contacts, events |
| `jobs` | job_id, job_title, job_type (ENUM), salary_min/max, job_url, date_posted, **requirements (JSON)** | FK to companies (ON DELETE CASCADE) |
| `applications` | application_id, application_date, status (ENUM), **current_round**, resume_version, cover_letter_sent, **interview_data (JSON)** | FK to jobs (ON DELETE CASCADE) |
| `contacts` | contact_id, contact_name, title, email, phone, linkedin_url, notes | FK to companies (ON DELETE CASCADE) |
| `events` | event_id, event_name, event_type (ENUM), event_date, location, notes | optional FK to companies (ON DELETE SET NULL) |

Also: a `CHECK` constraint so `salary_min <= salary_max`, and indexes on the foreign key columns.

## Setup Instructions

### 1. Prerequisites
- Python 3.10 or newer
- MySQL Server 8.0 or newer (running locally)
- Git

### 2. Clone the repository
```bash
git clone https://github.com/skyler-hall/job-application-tracker.git
cd job-application-tracker
```

### 3. Create the database
This creates the `job_tracker` database, all tables, and sample data.

**Mac/Linux:**
```bash
mysql -u root -p < schema.sql
```
**Windows (PowerShell):**
```powershell
mysql -u root -p -e "source schema.sql"
```
Or open `schema.sql` in **MySQL Workbench** and click the lightning bolt to run it.

> If `mysql` is not recognized on Windows, add MySQL to your PATH for the session:
> `$env:Path += ";C:\Program Files\MySQL\MySQL Server 8.0\bin"`

### 4. Set up Python
**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
> If PowerShell blocks the activate script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

### 5. Add your database password
Copy the example settings file and put in your own MySQL password:

**Mac/Linux:** `cp .env.example .env`  
**Windows:** `copy .env.example .env`

Then edit `.env`:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=job_tracker
```
`.env` is listed in `.gitignore`, so your password is never committed.

### 6. Run the app
```bash
python app.py
```
Open **http://127.0.0.1:5000** in your browser.

### 7. Run the tests (optional)
```bash
python -m unittest
```

## Project Structure

```
job-application-tracker/
├── app.py              # Flask routes for every page
├── database.py         # MySQL connection + all SQL queries
├── validators.py       # Form validation for every table
├── matching.py         # Job Match algorithm
├── schema.sql          # Creates the database, tables, and sample data
├── requirements.txt    # Python dependencies
├── .env.example        # Template for database settings
├── AI_USAGE.md         # How I used GenAI tools
├── templates/          # Jinja2 HTML templates (base layout + pages for each table)
├── static/style.css    # Styles (black, purple, pink, lime, and orange theme)
└── tests/              # Unit tests for the Job Match algorithm
```

## Security Notes

- Every SQL query uses **parameterized queries** (`%s` placeholders), which prevents SQL injection.
- Delete actions only work through **POST** requests, so a link can't delete data by accident.
- Database credentials live in `.env`, which is never committed.
- Jinja2 auto-escapes all output, which helps prevent cross-site scripting (XSS).

## How Job Match Works

1. You enter skills, like `Python, SQL, Flask`.
2. Each skill is normalized: lowercase, extra spaces removed, and common nicknames mapped (`JS` to `JavaScript`).
3. For each job, **match % = required skills you have / total required skills**.
4. Jobs are sorted by highest %, and ties go to the job where you match more skills.
5. Each result shows matched skills, missing skills, and a button to start tracking an application.

Example with `Python, SQL, Flask`: Software Developer at TechCorp is **100%** (3/3).
Data Analyst at DataCo is **67%** (2/3), missing Tableau.

## Future Improvements

## Future Improvements

- **Refactor the CRUD code.** I plan to refactor this in the future. Right now each table repeats the
  same route, query, and template pattern. My plan:
  - Pull the shared add/edit flow (validate, show errors, save, redirect) into one helper function
  - Split `app.py` into Flask Blueprints, one per table
  - Try SQLAlchemy and WTForms to cut down on hand-written INSERT/UPDATE statements and form code
  - Use Jinja macros for repeated form fields and table rows
- User accounts so more than one person can use it.
- Weighted Job Match (required vs. nice-to-have skills).
- Reminders for upcoming interviews and events.