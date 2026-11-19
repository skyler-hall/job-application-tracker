"""Job Application Tracker - Flask web application."""
import os

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


if __name__ == "__main__":
    app.run(debug=True)