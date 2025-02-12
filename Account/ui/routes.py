from flask import Blueprint, render_template

ui_bp = Blueprint('account_ui', __name__, template_folder="../templates")

@ui_bp.route('/account')
def account_page():
    return render_template('account.html')