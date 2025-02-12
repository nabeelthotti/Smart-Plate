from flask import Flask, session
from flask_cors import CORS
from LoginPage.api.auth import auth_bp as login_api_bp
from LoginPage.ui import ui_bp as login_ui_bp
from Dashboard.api.dashboard_routes import dashboard_api_bp
from Dashboard.ui.routes import ui_bp as dashboard_ui_bp
from Account.api.account_routes import account_api_bp
from Account.ui.routes import ui_bp as account_ui_bp
import os

app = Flask(__name__)
CORS(app)

# Secret Key for Sessions
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# Register Blueprints
app.register_blueprint(login_api_bp, url_prefix="/api")
app.register_blueprint(login_ui_bp)
app.register_blueprint(dashboard_api_bp, url_prefix="/dashboard-api")
app.register_blueprint(dashboard_ui_bp)
app.register_blueprint(account_api_bp, url_prefix="/account-api")
app.register_blueprint(account_ui_bp)

if __name__ == "__main__":
    app.run(debug=True)
