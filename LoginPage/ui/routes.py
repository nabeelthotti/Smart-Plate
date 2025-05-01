# LoginPage/ui/routes.py
import os
import requests
from flask import (
    Blueprint, render_template,
    session, redirect, url_for,
    request
)

login_ui_bp = Blueprint(
    "login_ui",
    __name__,
    template_folder="templates",
    static_folder="../static",
    static_url_path="/static"
)

API_BASE = os.getenv("API_BASE", "")

@login_ui_bp.route("/", methods=["GET", "POST"])
@login_ui_bp.route("/login", methods=["GET", "POST"])
def login_page():
    if session.get("username"):
        return redirect(url_for("dashboard_ui.dashboard"))

    error = None
    if request.method == "POST":
        # ... authenticate as before ...
        if resp.ok:
            session["username"] = username
            return redirect(url_for("dashboard_ui.dashboard"))
        else:
            error = data.get("message", "Login failed.")

    return render_template("login.html", mode="login", error=error)


@login_ui_bp.route("/signup", methods=["GET", "POST"])
def signup_page():
    if session.get("username"):
        return redirect(url_for("dashboard_ui.dashboard"))

    error = None
    if request.method == "POST":
        # ... register as before ...
        if resp.status_code == 201:
            session["username"] = username
            return redirect(url_for("dashboard_ui.dashboard"))
        else:
            error = data.get("message", "Signup failed.")

    return render_template("login.html", mode="signup", error=error)


@login_ui_bp.route("/scan", methods=["GET"])
def show_scan():
    return render_template("scan.html")
