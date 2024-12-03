from flask import Blueprint, render_template

ui_bp = Blueprint("dashboard_ui", __name__, template_folder="../templates", static_folder="../static")

@ui_bp.route("/dashboard")
def dashboard():
    # Render the `dashboard.html` template
    return render_template("dashboard.html")
