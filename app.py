import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

from utils.timezone_utils import (
    format_appointment_ist,
    format_appointment_ist_date,
    format_appointment_ist_time,
)

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Expose this module as `app` too, so `python app.py` and `gunicorn app:app`
# share one SQLAlchemy instance.
sys.modules.setdefault("app", sys.modules[__name__])

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback_dev_key")

    # Vercel's filesystem is read-only except /tmp, so use a temp SQLite file there.
    # Set DATABASE_URL (e.g. a free Postgres) to keep data permanently.
    on_vercel = bool(os.getenv("VERCEL"))
    default_db = "sqlite:////tmp/appointment.db" if on_vercel else "sqlite:///appointment.db"
    database_url = os.getenv("DATABASE_URL", default_db)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    # Imported here to avoid circular imports.
    from models import User
    from routes.auth import auth_bp
    from routes.doctor import doctor_bp
    from routes.patient import patient_bp

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    app.jinja_env.globals.update(
        format_appointment_ist=format_appointment_ist,
        format_appointment_ist_date=format_appointment_ist_date,
        format_appointment_ist_time=format_appointment_ist_time,
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)

    @app.route("/")
    def home():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("auth.login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        """Send each user to the dashboard for their role."""
        if current_user.role == "patient":
            return redirect(url_for("patient.dashboard"))
        if current_user.role == "doctor":
            return redirect(url_for("doctor.dashboard"))
        return redirect(url_for("auth.login"))

    with app.app_context():
        db.create_all()
        # Demo doctors + patient so a fresh deployment is not empty.
        if on_vercel or os.getenv("SEED_DEMO") == "1":
            _seed_demo_data()

    return app


def _seed_demo_data() -> None:
    """Add a few doctors and one demo patient if none exist yet."""
    from models import User

    if User.query.filter_by(role="doctor").first():
        return

    password_hash = generate_password_hash("Demo@1234")
    demo_users = [
        ("Dr. Aarav Mehta", "aarav.mehta@demo.com", "doctor"),
        ("Dr. Priya Sharma", "priya.sharma@demo.com", "doctor"),
        ("Dr. Rohan Verma", "rohan.verma@demo.com", "doctor"),
        ("Demo Patient", "patient@demo.com", "patient"),
    ]
    for name, email, role in demo_users:
        if not User.query.filter_by(email=email).first():
            db.session.add(User(
                full_name=name, email=email, role=role,
                doctor_status="approved", password_hash=password_hash,
            ))
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()


# WSGI entrypoint, e.g. `gunicorn app:app` (Vercel finds this too).
app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=debug)
