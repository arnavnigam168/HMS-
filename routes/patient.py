from flask import Blueprint, jsonify, render_template, request

from models import Patient, db
from routes.auth import login_required

patient_bp = Blueprint("patient", __name__, url_prefix="/patients")


@patient_bp.route("", methods=["GET"])
@login_required
def patients_page():
    return render_template("patients.html")


@patient_bp.route("/api", methods=["GET"])
@login_required
def list_patients():
    patients = Patient.query.order_by(Patient.id.desc()).all()
    return jsonify(
        [
            {
                "id": p.id,
                "name": p.name,
                "age": p.age,
                "gender": p.gender,
                "phone": p.phone,
                "disease": p.disease,
            }
            for p in patients
        ]
    )


@patient_bp.route("/api", methods=["POST"])
@login_required
def add_patient():
    try:
        payload = request.get_json(force=True)
        name = payload.get("name", "").strip()
        age = int(payload.get("age", 0))
        gender = payload.get("gender", "").strip()
        phone = payload.get("phone", "").strip()
        disease = payload.get("disease", "").strip()

        if not all([name, age, gender, phone, disease]):
            return jsonify({"error": "All fields are required."}), 400

        patient = Patient(name=name, age=age, gender=gender, phone=phone, disease=disease)
        db.session.add(patient)
        db.session.commit()
        print(f"[DEBUG] Added patient: {patient.name}")
        return jsonify({"message": "Patient added successfully."}), 201
    except ValueError:
        return jsonify({"error": "Age must be a valid number."}), 400
    except Exception as exc:
        db.session.rollback()
        print(f"[ERROR] add_patient failed: {exc}")
        return jsonify({"error": "Failed to add patient."}), 500


@patient_bp.route("/api/<int:patient_id>", methods=["DELETE"])
@login_required
def delete_patient(patient_id):
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({"error": "Patient not found."}), 404

        db.session.delete(patient)
        db.session.commit()
        print(f"[DEBUG] Deleted patient id={patient_id}")
        return jsonify({"message": "Patient deleted successfully."})
    except Exception as exc:
        db.session.rollback()
        print(f"[ERROR] delete_patient failed: {exc}")
        return jsonify({"error": "Failed to delete patient."}), 500
