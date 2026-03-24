from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models import User

auth_bp = Blueprint("auth", __name__)


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)

    return wrapper


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("login.html")

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash("Invalid credentials.", "danger")
            return render_template("login.html")

        session["username"] = user.username
        session["role"] = user.role
        print(f"[DEBUG] User logged in: {user.username} ({user.role})")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    username = session.get("username", "unknown")
    session.clear()
    print(f"[DEBUG] User logged out: {username}")
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))
