import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager

from backend.config import Config
from backend.models import db, User
from backend.routes.auth             import auth_bp
from backend.routes.dashboard        import dashboard_bp
from backend.routes.crops            import crops_bp
from backend.routes.disease          import disease_bp
from backend.routes.environment      import environment_bp
from backend.routes.yield_prediction import yield_bp
from backend.routes.recommendations  import recommendations_bp
from backend.routes.reports          import reports_bp


def create_app():
    app = Flask(
        __name__,
        template_folder = os.path.join('frontend', 'templates'),
        static_folder   = os.path.join('frontend', 'static'),
    )
    app.config.from_object(Config)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ── Database ───────────────────────────────────────────────────────────
    db.init_app(app)

    # ── Login Manager ──────────────────────────────────────────────────────
    login_manager = LoginManager()
    login_manager.login_view    = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ── Register blueprints ────────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(crops_bp)
    app.register_blueprint(disease_bp)
    app.register_blueprint(environment_bp)
    app.register_blueprint(yield_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(reports_bp)

    # ── Landing page ───────────────────────────────────────────────────────
    @app.route('/')
    def landing():
        return render_template('landing.html')

    # ── Create tables if they don't exist ──────────────────────────────────
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.warning(f"DB init warning: {e}")

    return app


if __name__ == '__main__':
    application = create_app()
    application.run(debug=True, host='0.0.0.0', port=5000)
