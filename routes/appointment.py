from datetime import datetime

from flask import Blueprint, jsonify, render_template, request

from models import Appointment, Bill, Doctor, Patient, db
from routes.auth import login_required

appointment_bp = Blueprint("appointment", __name__, url_prefix="/appointments")


@appointment_bp.route("", methods=["GET"])
@login_required
def appointments_page():
    return render_template("appointments.html")


@appointment_bp.route("/api/meta", methods=["GET"])
@login_required
def appointment_meta():
    patients = Patient.query.order_by(Patient.name.asc()).all()
    doctors = Doctor.query.order_by(Doctor.name.asc()).all()
    return jsonify(
        {
            "patients": [{"id": p.id, "name": p.name} for p in patients],
            "doctors": [{"id": d.id, "name": d.name} for d in doctors],
        }
    )


@appointment_bp.route("/api", methods=["GET"])
@login_required
def list_appointments():
    appointments = Appointment.query.order_by(Appointment.appointment_datetime.desc()).all()
    return jsonify(
        [
            {
                "id": a.id,
                "patient_id": a.patient_id,
                "patient_name": a.patient.name,
                "doctor_id": a.doctor_id,
                "doctor_name": a.doctor.name,
                "appointment_datetime": a.appointment_datetime.strftime("%Y-%m-%d %H:%M"),
                "has_bill": a.bill is not None,
            }
            for a in appointments
        ]
    )


@appointment_bp.route("/api", methods=["POST"])
@login_required
def add_appointment():
    try:
        payload = request.get_json(force=True)
        patient_id = int(payload.get("patient_id", 0))
        doctor_id = int(payload.get("doctor_id", 0))
        dt_str = payload.get("appointment_datetime", "").strip()

        if not all([patient_id, doctor_id, dt_str]):
            return jsonify({"error": "All fields are required."}), 400

        patient = Patient.query.get(patient_id)
        doctor = Doctor.query.get(doctor_id)
        if not patient or not doctor:
            return jsonify({"error": "Invalid patient or doctor selection."}), 400

        appointment_dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")

        duplicate = Appointment.query.filter_by(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_datetime=appointment_dt,
        ).first()
        if duplicate:
            return jsonify({"error": "Duplicate appointment booking detected."}), 409

        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_datetime=appointment_dt,
        )
        db.session.add(appointment)
        db.session.commit()
        print(f"[DEBUG] Booked appointment id={appointment.id}")
        return jsonify({"message": "Appointment booked successfully."}), 201
    except ValueError:
        return jsonify({"error": "Invalid date/time format."}), 400
    except Exception as exc:
        db.session.rollback()
        print(f"[ERROR] add_appointment failed: {exc}")
        return jsonify({"error": "Failed to book appointment."}), 500


@appointment_bp.route("/bills/api", methods=["GET"])
@login_required
def list_bills():
    bills = Bill.query.order_by(Bill.id.desc()).all()
    return jsonify(
        [
            {
                "id": b.id,
                "appointment_id": b.appointment_id,
                "patient_name": b.patient.name,
                "consultation_fee": b.consultation_fee,
                "medicine_fee": b.medicine_fee,
                "test_fee": b.test_fee,
                "total_amount": b.total_amount,
            }
            for b in bills
        ]
    )


@appointment_bp.route("/bills/api", methods=["POST"])
@login_required
def generate_bill():
    try:
        payload = request.get_json(force=True)
        appointment_id = int(payload.get("appointment_id", 0))
        consultation_fee = float(payload.get("consultation_fee", 0))
        medicine_fee = float(payload.get("medicine_fee", 0))
        test_fee = float(payload.get("test_fee", 0))

        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({"error": "Appointment not found."}), 404
        if appointment.bill:
            return jsonify({"error": "Bill already exists for this appointment."}), 409
        if consultation_fee < 0 or medicine_fee < 0 or test_fee < 0:
            return jsonify({"error": "Fee values cannot be negative."}), 400

        total = round(consultation_fee + medicine_fee + test_fee, 2)
        bill = Bill(
            appointment_id=appointment.id,
            patient_id=appointment.patient_id,
            consultation_fee=consultation_fee,
            medicine_fee=medicine_fee,
            test_fee=test_fee,
            total_amount=total,
        )
        db.session.add(bill)
        db.session.commit()
        print(f"[DEBUG] Generated bill id={bill.id} for appointment={appointment.id}")
        return jsonify({"message": "Bill generated successfully.", "total_amount": total}), 201
    except ValueError:
        return jsonify({"error": "Invalid numeric values in billing form."}), 400
    except Exception as exc:
        db.session.rollback()
        print(f"[ERROR] generate_bill failed: {exc}")
        return jsonify({"error": "Failed to generate bill."}), 500
