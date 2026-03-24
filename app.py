from pathlib import Path

from flask import Flask, redirect, render_template, session, url_for

from models import Appointment, Doctor, Patient, User, db
from routes.ai import ai_bp
from routes.appointment import appointment_bp
from routes.auth import auth_bp, login_required
from routes.doctor import doctor_bp
from routes.patient import patient_bp


def seed_data():
    if not User.query.first():
        admin = User(username="admin", role="admin")
        admin.set_password("admin123")
        staff = User(username="staff", role="staff")
        staff.set_password("staff123")
        db.session.add_all([admin, staff])
        print("[DEBUG] Seeded default users.")

    if not Patient.query.first():
        patients = [
            Patient(name="Arun Kumar", age=34, gender="Male", phone="9876543210", disease="Flu"),
            Patient(name="Neha Singh", age=28, gender="Female", phone="9123456780", disease="Migraine"),
        ]
        db.session.add_all(patients)
        print("[DEBUG] Seeded sample patients.")

    if not Doctor.query.first():
        doctors = [
            Doctor(name="Dr. Meera Sharma", specialization="General Medicine", availability="Mon-Fri 10 AM-2 PM"),
            Doctor(name="Dr. Raj Verma", specialization="Neurology", availability="Tue-Sat 1 PM-5 PM"),
        ]
        db.session.add_all(doctors)
        print("[DEBUG] Seeded sample doctors.")

    db.session.commit()

    if not Appointment.query.first():
        p = Patient.query.first()
        d = Doctor.query.first()
        if p and d:
            from datetime import datetime, timedelta

            appt = Appointment(
                patient_id=p.id,
                doctor_id=d.id,
                appointment_datetime=datetime.now() + timedelta(days=1),
            )
            db.session.add(appt)
            db.session.commit()
            print("[DEBUG] Seeded sample appointment.")


def create_app():
    app = Flask(__name__)
    db_path = Path(__file__).resolve().parent / "database.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path.as_posix()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "hms-super-secret-key-change-in-production"

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(ai_bp)

    @app.route("/")
    def home():
        if "username" in session:
            return redirect(url_for("dashboard"))
        return redirect(url_for("auth.login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.html", username=session.get("username"), role=session.get("role"))

    with app.app_context():
        db.create_all()
        seed_data()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
