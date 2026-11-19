"""Job Application Tracker - Flask web application."""
import os
from datetime import date

from flask import Flask, abort, flash, redirect, render_template, request, url_for
from mysql.connector import IntegrityError

import database as db
import validators as v

app = Flask(__name__)
# Needed for flash() messages. Set SECRET_KEY in .env for a real deployment.
app.secret_key = os.getenv("SECRET_KEY", "dev-only-secret")


@app.route("/")
def dashboard():
    stats = db.get_dashboard_stats()
    return render_template("dashboard.html", statuses=db.STATUSES, **stats)




# ---------------------------------------------------------------------
# Companies
# ---------------------------------------------------------------------

@app.route("/companies")
def companies():
    search = request.args.get("q", "").strip()
    return render_template("companies.html", companies=db.get_companies(search), search=search)


@app.route("/companies/<int:company_id>")
def company_detail(company_id):
    company = db.get_company(company_id) or abort(404)
    return render_template("company_detail.html", company=company,
                           **db.get_company_related(company_id))


@app.route("/companies/new", methods=["GET", "POST"])
def company_new():
    if request.method == "POST":
        data, errors = v.validate_company(request.form)
        if not errors:
            try:
                new_id = db.create_company(data)
                flash(f"Added {data['company_name']}.", "success")
                return redirect(url_for("company_detail", company_id=new_id))
            except IntegrityError:
                errors.append(f"A company named {data['company_name']} already exists.")
        for error in errors:
            flash(error, "error")
        # Re-show the form with what the user typed so they don't lose it
        return render_template("company_form.html", company=data, is_edit=False)
    return render_template("company_form.html", company={}, is_edit=False)


@app.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
def company_edit(company_id):
    company = db.get_company(company_id) or abort(404)
    if request.method == "POST":
        data, errors = v.validate_company(request.form)
        if not errors:
            try:
                db.update_company(company_id, data)
                flash(f"Updated {data['company_name']}.", "success")
                return redirect(url_for("company_detail", company_id=company_id))
            except IntegrityError:
                errors.append(f"A company named {data['company_name']} already exists.")
        for error in errors:
            flash(error, "error")
        data["company_id"] = company_id
        return render_template("company_form.html", company=data, is_edit=True)
    return render_template("company_form.html", company=company, is_edit=True)


@app.route("/companies/<int:company_id>/delete", methods=["POST"])
def company_delete(company_id):
    company = db.get_company(company_id) or abort(404)
    db.delete_company(company_id)
    flash(f"Deleted {company['company_name']} and its jobs, applications, and contacts.", "success")
    return redirect(url_for("companies"))

# ---------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------

def _job_form(job, is_edit):
    return render_template("job_form.html", job=job, is_edit=is_edit,
                           companies=db.get_company_choices(), job_types=v.JOB_TYPES)


@app.route("/jobs")
def jobs():
    search = request.args.get("q", "").strip()
    job_type = request.args.get("type", "").strip()
    return render_template("jobs.html", jobs=db.get_jobs(search, job_type),
                           search=search, job_type=job_type, job_types=v.JOB_TYPES)


@app.route("/jobs/<int:job_id>")
def job_detail(job_id):
    job = db.get_job(job_id) or abort(404)
    return render_template("job_detail.html", job=job,
                           applications=db.get_job_applications(job_id))


@app.route("/jobs/new", methods=["GET", "POST"])
def job_new():
    if request.method == "POST":
        company_ids = {c["company_id"] for c in db.get_company_choices()}
        data, errors = v.validate_job(request.form, company_ids)
        if not errors:
            new_id = db.create_job(data)
            flash(f"Added {data['job_title']}.", "success")
            return redirect(url_for("job_detail", job_id=new_id))
        for error in errors:
            flash(error, "error")
        return _job_form(data, is_edit=False)
    # Pre-select a company when coming from a company's page (?company_id=3)
    return _job_form({"company_id": request.args.get("company_id")}, is_edit=False)


@app.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
def job_edit(job_id):
    job = db.get_job(job_id) or abort(404)
    if request.method == "POST":
        company_ids = {c["company_id"] for c in db.get_company_choices()}
        data, errors = v.validate_job(request.form, company_ids)
        if not errors:
            db.update_job(job_id, data)
            flash(f"Updated {data['job_title']}.", "success")
            return redirect(url_for("job_detail", job_id=job_id))
        for error in errors:
            flash(error, "error")
        data["job_id"] = job_id
        return _job_form(data, is_edit=True)
    return _job_form(job, is_edit=True)


@app.route("/jobs/<int:job_id>/delete", methods=["POST"])
def job_delete(job_id):
    job = db.get_job(job_id) or abort(404)
    db.delete_job(job_id)
    flash(f"Deleted {job['job_title']} and its applications.", "success")
    return redirect(url_for("jobs"))

# ---------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------

def _application_form(application, is_edit):
    # Show the saved interview rounds plus empty rows to add more (at least 3 rows)
    rows = list(application.get("interviews") or [])
    rows += [{}] * max(3 - len(rows), 1)
    return render_template("application_form.html", application=application, is_edit=is_edit,
                           jobs=db.get_job_choices(), statuses=v.STATUSES,
                           interview_types=v.INTERVIEW_TYPES, interview_rows=rows)


@app.route("/applications")
def applications():
    status = request.args.get("status", "").strip()
    search = request.args.get("q", "").strip()
    return render_template("applications.html", applications=db.get_applications(status, search),
                           status=status, search=search, statuses=v.STATUSES)


@app.route("/applications/<int:application_id>")
def application_detail(application_id):
    application = db.get_application(application_id) or abort(404)
    return render_template("application_detail.html", application=application)


@app.route("/applications/new", methods=["GET", "POST"])
def application_new():
    if request.method == "POST":
        job_ids = {j["job_id"] for j in db.get_job_choices()}
        data, errors = v.validate_application(request.form, job_ids)
        if not errors:
            new_id = db.create_application(data)
            flash("Application added.", "success")
            return redirect(url_for("application_detail", application_id=new_id))
        for error in errors:
            flash(error, "error")
        return _application_form(data, is_edit=False)
    # Default to today's date, and pre-select a job when coming from a job page (?job_id=2)
    return _application_form({"job_id": request.args.get("job_id"),
                              "application_date": date.today().isoformat(),
                              "status": "Applied"}, is_edit=False)


@app.route("/applications/<int:application_id>/edit", methods=["GET", "POST"])
def application_edit(application_id):
    application = db.get_application(application_id) or abort(404)
    if request.method == "POST":
        job_ids = {j["job_id"] for j in db.get_job_choices()}
        data, errors = v.validate_application(request.form, job_ids)
        if not errors:
            db.update_application(application_id, data)
            flash("Application updated.", "success")
            return redirect(url_for("application_detail", application_id=application_id))
        for error in errors:
            flash(error, "error")
        data["application_id"] = application_id
        return _application_form(data, is_edit=True)
    return _application_form(application, is_edit=True)


@app.route("/applications/<int:application_id>/delete", methods=["POST"])
def application_delete(application_id):
    db.get_application(application_id) or abort(404)
    db.delete_application(application_id)
    flash("Application deleted.", "success")
    return redirect(url_for("applications"))

# ---------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------

def _contact_form(contact, is_edit):
    return render_template("contact_form.html", contact=contact, is_edit=is_edit,
                           companies=db.get_company_choices())


@app.route("/contacts")
def contacts():
    search = request.args.get("q", "").strip()
    return render_template("contacts.html", contacts=db.get_contacts(search), search=search)


@app.route("/contacts/<int:contact_id>")
def contact_detail(contact_id):
    contact = db.get_contact(contact_id) or abort(404)
    return render_template("contact_detail.html", contact=contact)


@app.route("/contacts/new", methods=["GET", "POST"])
def contact_new():
    if request.method == "POST":
        company_ids = {c["company_id"] for c in db.get_company_choices()}
        data, errors = v.validate_contact(request.form, company_ids)
        if not errors:
            new_id = db.create_contact(data)
            flash(f"Added {data['contact_name']}.", "success")
            return redirect(url_for("contact_detail", contact_id=new_id))
        for error in errors:
            flash(error, "error")
        return _contact_form(data, is_edit=False)
    return _contact_form({"company_id": request.args.get("company_id")}, is_edit=False)


@app.route("/contacts/<int:contact_id>/edit", methods=["GET", "POST"])
def contact_edit(contact_id):
    contact = db.get_contact(contact_id) or abort(404)
    if request.method == "POST":
        company_ids = {c["company_id"] for c in db.get_company_choices()}
        data, errors = v.validate_contact(request.form, company_ids)
        if not errors:
            db.update_contact(contact_id, data)
            flash(f"Updated {data['contact_name']}.", "success")
            return redirect(url_for("contact_detail", contact_id=contact_id))
        for error in errors:
            flash(error, "error")
        data["contact_id"] = contact_id
        return _contact_form(data, is_edit=True)
    return _contact_form(contact, is_edit=True)


@app.route("/contacts/<int:contact_id>/delete", methods=["POST"])
def contact_delete(contact_id):
    contact = db.get_contact(contact_id) or abort(404)
    db.delete_contact(contact_id)
    flash(f"Deleted {contact['contact_name']}.", "success")
    return redirect(url_for("contacts"))

if __name__ == "__main__":
    app.run(debug=True)