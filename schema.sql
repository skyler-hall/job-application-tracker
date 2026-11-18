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
CREATE TABLE applications (
    application_id    INT PRIMARY KEY AUTO_INCREMENT,
    job_id            INT NOT NULL,
    application_date  DATE NOT NULL,
    status            ENUM('Applied','Screening','Interview','Offer','Rejected','Withdrawn')
                      NOT NULL DEFAULT 'Applied',
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