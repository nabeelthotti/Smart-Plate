from flask import Flask
from flask_cors import CORS
from LoginPage.api import api_bp as login_api_bp
from LoginPage.ui import ui_bp as login_ui_bp
from Dashboard.api.dashboard_routes import dashboard_api_bp
from Dashboard.ui.routes import ui_bp as dashboard_ui_bp

# Initialize Flask app
app = Flask(
    __name__,
    static_folder="LoginPage/static",   # Explicitly set the static folder
    template_folder="LoginPage/templates",  # Explicitly set the templates folder
)
CORS(app)

# Register Blueprints
app.register_blueprint(login_api_bp, url_prefix="/api")
app.register_blueprint(login_ui_bp)
app.register_blueprint(dashboard_api_bp, url_prefix="/dashboard-api")  # Dashboard API
app.register_blueprint(dashboard_ui_bp)  # Dashboard UI

if __name__ == "__main__":
    app.run(debug=True)
