from datetime import date
from functools import wraps

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash
)

from app.db import get_db, init_db

bp = Blueprint("main", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)
    return wrapped


@bp.before_app_request
def setup():
    init_db()


@bp.route("/")
def login():
    if "user_id" in session:
        return redirect(url_for("main.dashboard"))
    return render_template("login.html")


@bp.route("/login", methods=["POST"])
def do_login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    ).fetchone()
    db.close()

    if user:
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        return redirect(url_for("main.dashboard"))

    flash("Username ya password ghalat hai.")
    return redirect(url_for("main.login"))


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@bp.route("/dashboard")
@login_required
def dashboard():
    selected_date = request.args.get(
        "date", date.today().isoformat()
    )

    db = get_db()

    companies = db.execute(
        "SELECT * FROM companies WHERE active=1 ORDER BY name"
    ).fetchall()

    payments = db.execute("""
        SELECT payments.*, companies.name AS company_name
        FROM payments
        LEFT JOIN companies ON companies.id = payments.company_id
        WHERE payment_date=?
        ORDER BY payments.id DESC
    """, (selected_date,)).fetchall()

    totals = db.execute("""
        SELECT
        COALESCE(SUM(expected),0) AS expected,
        COALESCE(SUM(paid),0) AS paid
        FROM payments
        WHERE payment_date=?
    """, (selected_date,)).fetchone()

    db.close()

    expected = float(totals["expected"] or 0)
    paid = float(totals["paid"] or 0)

    return render_template(
        "dashboard.html",
        companies=companies,
        payments=payments,
        selected_date=selected_date,
        expected=expected,
        paid=paid,
        difference=paid - expected
    )


@bp.route("/companies", methods=["GET", "POST"])
@login_required
def companies():
    db = get_db()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        expected = float(request.form.get("expected_amount") or 0)
        weekly = 1 if request.form.get("weekly") else 0
        weekday = int(request.form.get("weekday") or 0)

        if name:
            db.execute("""
                INSERT INTO companies
                (name, expected_amount, weekly, weekday)
                VALUES (?, ?, ?, ?)
            """, (name, expected, weekly, weekday))
            db.commit()
            flash("Company add ho gayi.")

    rows = db.execute(
        "SELECT * FROM companies ORDER BY name"
    ).fetchall
