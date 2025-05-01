from flask import Blueprint, render_template, session, redirect, url_for

dashboard_ui_bp = Blueprint("dashboard_ui", __name__, template_folder="templates")

@dashboard_ui_bp.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("dashboard_ui.dashboard"))
    return render_template('dashboard.html')