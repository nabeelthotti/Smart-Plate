from flask import render_template

from . import ui_bp

@ui_bp.route("/")
def index():
    return render_template("index.html")
