-- Job Application Tracker - Database Creation Script
-- Run with: mysql -u root -p -e "source schema.sql"

DROP DATABASE IF EXISTS job_tracker;
CREATE DATABASE job_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE job_tracker;

-- companies: one row per employer
CREATE TABLE companies (
    company_id   INT PRIMARY KEY AUTO_INCREMENT,
    company_name VARCHAR(100) NOT NULL,
    industry     VARCHAR(50),
    website      VARCHAR(200),
    city         VARCHAR(50),
    state        VARCHAR(50),
    notes        TEXT,
    CONSTRAINT uq_company_name UNIQUE (company_name)
);

-- jobs: a posting at a company
-- requirements is a JSON array of skills, e.g. ["Python", "SQL"]
CREATE TABLE jobs (
    job_id       INT PRIMARY KEY AUTO_INCREMENT,
    company_id   INT NOT NULL,
    job_title    VARCHAR(100) NOT NULL,
    job_type     ENUM('Full-time', 'Part-time', 'Contract', 'Internship'),
    salary_min   INT,
    salary_max   INT,
    job_url      VARCHAR(300),
    date_posted  DATE,
    requirements JSON,
    CONSTRAINT fk_jobs_company FOREIGN KEY (company_id)
        REFERENCES companies (company_id) ON DELETE CASCADE,
    CONSTRAINT chk_salary_range
        CHECK (salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max)
);

-- applications: each time I apply to a job
-- interview_data is a JSON array of interview rounds
-- current_round: 0 = no interviews yet
CREATE TABLE applications (
    application_id    INT PRIMARY KEY AUTO_INCREMENT,
    job_id            INT NOT NULL,
    application_date  DATE NOT NULL,
    status            ENUM('Applied','Screening','Interview','Offer','Rejected','Withdrawn')
                      NOT NULL DEFAULT 'Applied',
    current_round     TINYINT UNSIGNED NOT NULL DEFAULT 0,
    resume_version    VARCHAR(50),
    cover_letter_sent BOOLEAN NOT NULL DEFAULT FALSE,
    interview_data    JSON,
    CONSTRAINT fk_applications_job FOREIGN KEY (job_id)
        REFERENCES jobs (job_id) ON DELETE CASCADE
);

-- contacts: people I know at a company
CREATE TABLE contacts (
    contact_id   INT PRIMARY KEY AUTO_INCREMENT,
    company_id   INT NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    title        VARCHAR(100),
    email        VARCHAR(100),
    phone        VARCHAR(20),
    linkedin_url VARCHAR(200),
    notes        TEXT,
    CONSTRAINT fk_contacts_company FOREIGN KEY (company_id)
        REFERENCES companies (company_id) ON DELETE CASCADE
);

-- events: career fairs, info sessions, networking, etc.
-- company_id is optional since some events have many companies
CREATE TABLE events (
    event_id    INT PRIMARY KEY AUTO_INCREMENT,
    company_id  INT,
    event_name  VARCHAR(100) NOT NULL,
    event_type  ENUM('Career Fair','Info Session','Networking','Workshop','Conference','Other'),
    event_date  DATE NOT NULL,
    location    VARCHAR(100),
    notes       TEXT,
    CONSTRAINT fk_events_company FOREIGN KEY (company_id)
        REFERENCES companies (company_id) ON DELETE SET NULL
);

-- =====================================================================
-- Sample data
-- =====================================================================

INSERT INTO companies (company_name, industry, website, city, state, notes) VALUES
('TechCorp',        'Software',           'https://www.techcorp.example',       'Miami',           'FL', 'Mid-size SaaS company. Strong Python shop.'),
('DataCo',          'Analytics',          'https://www.dataco.example',         'Fort Lauderdale', 'FL', 'Heavy on dashboards and BI tools.'),
('Capital One',     'Financial Services', 'https://www.capitalone.com',         'Richmond',        'VA', 'Technology Development Program.'),
('Bright Robotics', 'Robotics',           'https://www.brightrobotics.example', 'Pittsburgh',      'PA', 'Field robots for environmental monitoring.'),
('Sunshine Health', 'Healthcare',         'https://www.sunshinehealth.example', 'Orlando',         'FL', NULL);

INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements) VALUES
(1, 'Software Developer',          'Full-time',   85000, 105000, 'https://www.techcorp.example/careers/101',  '2026-09-01', '["Python", "SQL", "Flask"]'),
(2, 'Data Analyst',                'Full-time',   65000,  80000, 'https://www.dataco.example/jobs/22',        '2026-09-10', '["Python", "SQL", "Tableau"]'),
(3, 'Associate Software Engineer', 'Full-time',  110000, 130000, 'https://www.capitalone.com/careers',        '2026-08-15', '["Java", "Python", "AWS", "SQL", "Git"]'),
(4, 'Robotics Software Intern',    'Internship',  25000,  35000, 'https://www.brightrobotics.example/intern', '2026-10-05', '["Python", "ROS", "C++", "Linux"]'),
(5, 'Junior Web Developer',        'Contract',    50000,  60000, 'https://www.sunshinehealth.example/jobs/7', '2026-10-20', '["HTML", "CSS", "JavaScript", "Flask"]'),
(1, 'Database Administrator',      'Part-time',   40000,  50000, NULL,                                         '2026-11-01', '["MySQL", "SQL", "Linux"]');

INSERT INTO applications (job_id, application_date, status, current_round, resume_version, cover_letter_sent, interview_data) VALUES
(1, '2026-09-05', 'Interview', 2, 'SWE_v3', TRUE,
    '[{"round": 1, "date": "2026-09-20", "type": "Phone", "interviewer": "Maria Lopez", "notes": "Talked about Flask projects"},
      {"round": 2, "date": "2026-12-02", "type": "Technical", "interviewer": "Dev Patel", "notes": "Live coding, SQL joins"}]'),
(2, '2026-09-12', 'Rejected',  0, 'Data_v1',     FALSE, NULL),
(3, '2026-08-20', 'Offer',     1, 'SWE_v3',      TRUE,
    '[{"round": 1, "date": "2026-09-08", "type": "Powerday", "interviewer": "Panel", "notes": "Case study, behavioral, technical"}]'),
(4, '2026-10-08', 'Screening', 0, 'Robotics_v1', TRUE,  NULL),
(5, '2026-10-22', 'Applied',   0, 'Web_v2',      FALSE, NULL),
(6, '2026-11-03', 'Withdrawn', 0, 'SWE_v3',      FALSE, NULL);

INSERT INTO contacts (company_id, contact_name, title, email, phone, linkedin_url, notes) VALUES
(1, 'Maria Lopez', 'Technical Recruiter',    'maria.lopez@techcorp.example',  '305-555-0142', NULL, 'Met at a career fair.'),
(1, 'Dev Patel',   'Senior Engineer',        'dev.patel@techcorp.example',    NULL,           NULL, 'Ran my technical round.'),
(3, 'Jordan Reed', 'Recruiting Coordinator', 'jordan.reed@capitalone.example', '804-555-0199', NULL, 'Scheduled Powerday.'),
(4, 'Ana Ruiz',    'Engineering Manager',    'ana@brightrobotics.example',    NULL,           NULL, 'Interested in solar-powered robots.');

INSERT INTO events (company_id, event_name, event_type, event_date, location, notes) VALUES
(NULL, 'FIU Fall Career Fair',  'Career Fair',  '2026-09-24', 'FIU MMC',    'Bring 20 resumes.'),
(1,    'TechCorp Info Session', 'Info Session', '2026-10-15', 'Zoom',       'Ask about the new grad program.'),
(4,    'Robotics Meetup',       'Networking',   '2026-12-05', 'Miami, FL',  NULL);