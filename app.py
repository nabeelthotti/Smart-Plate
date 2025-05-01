import os
from flask import Flask, session, redirect, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from LoginPage.api.auth            import auth_bp   as login_api_bp
from LoginPage.api.scan_api        import scan_bp
from Dashboard.api.dashboard_routes import dashboard_api_bp
from LoginPage.ui.routes           import login_ui_bp
from Dashboard.ui.routes           import dashboard_ui_bp
from Account.api.account_routes    import account_api_bp
from Account.ui.routes             import ui_bp     as account_ui_bp

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

# — your existing blueprint registrations —
app.register_blueprint(login_api_bp,       url_prefix='/api')
app.register_blueprint(scan_bp,            url_prefix='/api')
app.register_blueprint(dashboard_api_bp,   url_prefix='/dashboard-api')
app.register_blueprint(login_ui_bp)        # serves /login, /signup, etc.
app.register_blueprint(dashboard_ui_bp)
app.register_blueprint(account_api_bp,     url_prefix='/account-api')
app.register_blueprint(account_ui_bp)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# — serve your swagger.yaml from the project root —
@app.route('/swagger.yaml')
def swagger_spec():
    return send_from_directory(app.root_path, 'swagger.yaml')

# — mount swagger-ui at /docs —
SWAGGER_URL = '/docs'              # URL for exposing Swagger UI (without trailing slash)
API_URL     = '/swagger.yaml'      # our spec file

swaggerui_bp = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={  
        'app_name': "Smart-Plate API Docs"
    }
)
app.register_blueprint(swaggerui_bp, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    app.run(debug=True)
