"""Job Application Tracker - Flask web application."""
import os

from flask import Flask, render_template

import database as db

app = Flask(__name__)
# Needed for flash() messages. Set SECRET_KEY in .env for a real deployment.
app.secret_key = os.getenv("SECRET_KEY", "dev-only-secret")


@app.route("/")
def dashboard():
    stats = db.get_dashboard_stats()
    return render_template("dashboard.html", statuses=db.STATUSES, **stats)


if __name__ == "__main__":
    app.run(debug=True)