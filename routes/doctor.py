from flask import Blueprint, jsonify, render_template, request

from models import Doctor, db
from routes.auth import login_required

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctors")


@doctor_bp.route("", methods=["GET"])
@login_required
def doctors_page():
    return render_template("doctors.html")


@doctor_bp.route("/api", methods=["GET"])
@login_required
def list_doctors():
    doctors = Doctor.query.order_by(Doctor.id.desc()).all()
    return jsonify(
        [
            {
                "id": d.id,
                "name": d.name,
                "specialization": d.specialization,
                "availability": d.availability,
            }
            for d in doctors
        ]
    )


@doctor_bp.route("/api", methods=["POST"])
@login_required
def add_doctor():
    try:
        payload = request.get_json(force=True)
        name = payload.get("name", "").strip()
        specialization = payload.get("specialization", "").strip()
        availability = payload.get("availability", "").strip()

        if not all([name, specialization, availability]):
            return jsonify({"error": "All fields are required."}), 400

        doctor = Doctor(name=name, specialization=specialization, availability=availability)
        db.session.add(doctor)
        db.session.commit()
        print(f"[DEBUG] Added doctor: {doctor.name}")
        return jsonify({"message": "Doctor added successfully."}), 201
    except Exception as exc:
        db.session.rollback()
        print(f"[ERROR] add_doctor failed: {exc}")
        return jsonify({"error": "Failed to add doctor."}), 500
