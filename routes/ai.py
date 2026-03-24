from collections import defaultdict
import re

from flask import Blueprint, jsonify, render_template, request

from routes.auth import login_required

ai_bp = Blueprint("ai", __name__)

SYMPTOM_ALIASES = {
    "high temperature": "fever",
    "temperature": "fever",
    "pyrexia": "fever",
    "runny nose": "nasal congestion",
    "blocked nose": "nasal congestion",
    "stuffy nose": "nasal congestion",
    "sore throat": "throat pain",
    "throat irritation": "throat pain",
    "head ache": "headache",
    "throwing up": "vomiting",
    "loose motion": "diarrhea",
    "loose motions": "diarrhea",
    "joint pain": "body pain",
    "muscle pain": "body pain",
    "chest tightness": "chest pain",
    "short breath": "shortness of breath",
    "breathlessness": "shortness of breath",
    "burning urination": "painful urination",
    "burning urine": "painful urination",
    "frequent urine": "frequent urination",
    "tiredness": "fatigue",
    "weakness": "fatigue",
}

# Rich rule-based symptom bank for broader prediction coverage.
DISEASE_SYMPTOM_WEIGHTS = {
    "viral fever": {"fever": 0.95, "body pain": 0.75, "fatigue": 0.8, "headache": 0.7, "chills": 0.7},
    "flu": {"fever": 0.9, "cough": 0.85, "headache": 0.7, "body pain": 0.8, "fatigue": 0.75, "throat pain": 0.7},
    "common cold": {"cough": 0.75, "sneezing": 0.9, "nasal congestion": 0.9, "throat pain": 0.6, "mild fever": 0.5},
    "typhoid": {"fever": 0.9, "abdominal pain": 0.7, "diarrhea": 0.7, "loss of appetite": 0.75, "fatigue": 0.7},
    "dengue": {"high fever": 0.95, "body pain": 0.9, "headache": 0.75, "rash": 0.7, "nausea": 0.65, "joint pain": 0.8},
    "malaria": {"fever": 0.9, "chills": 0.95, "sweating": 0.85, "headache": 0.65, "nausea": 0.6},
    "migraine": {"headache": 0.95, "nausea": 0.7, "vomiting": 0.65, "light sensitivity": 0.9, "blurred vision": 0.7},
    "sinusitis": {"headache": 0.7, "facial pain": 0.85, "nasal congestion": 0.9, "cough": 0.5, "throat pain": 0.5},
    "bronchitis": {"cough": 0.95, "chest discomfort": 0.8, "fatigue": 0.6, "mild fever": 0.5, "shortness of breath": 0.7},
    "pneumonia": {"fever": 0.85, "cough": 0.9, "chest pain": 0.85, "shortness of breath": 0.9, "chills": 0.7},
    "asthma": {"shortness of breath": 0.95, "wheezing": 0.9, "cough": 0.7, "chest tightness": 0.85},
    "gastritis": {"abdominal pain": 0.9, "nausea": 0.75, "vomiting": 0.7, "bloating": 0.75, "loss of appetite": 0.65},
    "food poisoning": {"nausea": 0.9, "vomiting": 0.9, "diarrhea": 0.9, "abdominal pain": 0.8, "fever": 0.45},
    "gastroenteritis": {"diarrhea": 0.9, "vomiting": 0.8, "abdominal pain": 0.8, "fever": 0.6, "dehydration": 0.7},
    "anemia": {"fatigue": 0.95, "pale skin": 0.8, "shortness of breath": 0.75, "dizziness": 0.8, "headache": 0.55},
    "hypothyroidism": {"fatigue": 0.85, "weight gain": 0.85, "cold intolerance": 0.8, "dry skin": 0.65, "constipation": 0.7},
    "hypertension": {"headache": 0.65, "dizziness": 0.7, "blurred vision": 0.75, "chest pain": 0.6, "nosebleed": 0.5},
    "diabetes": {"frequent urination": 0.9, "increased thirst": 0.9, "fatigue": 0.7, "blurred vision": 0.75, "weight loss": 0.65},
    "urinary tract infection": {"painful urination": 0.95, "frequent urination": 0.85, "lower abdominal pain": 0.75, "fever": 0.55},
    "kidney stone": {"severe flank pain": 0.95, "painful urination": 0.7, "nausea": 0.6, "blood in urine": 0.85},
    "allergic rhinitis": {"sneezing": 0.95, "nasal congestion": 0.9, "itchy eyes": 0.85, "runny nose": 0.9},
    "conjunctivitis": {"red eyes": 0.95, "itchy eyes": 0.85, "eye discharge": 0.9, "watering eyes": 0.85},
    "covid-19": {"fever": 0.8, "dry cough": 0.85, "shortness of breath": 0.8, "loss of taste": 0.95, "loss of smell": 0.95, "fatigue": 0.7},
}

SYMPTOM_DISEASE_MAP = defaultdict(dict)
for disease, symptom_weights in DISEASE_SYMPTOM_WEIGHTS.items():
    for symptom, score in symptom_weights.items():
        canonical_symptom = symptom.strip().lower()
        SYMPTOM_DISEASE_MAP[canonical_symptom][disease] = score


def normalize_symptom(symptom: str) -> str:
    cleaned = re.sub(r"\s+", " ", symptom.strip().lower())
    return SYMPTOM_ALIASES.get(cleaned, cleaned)


def match_symptom(symptom: str) -> str | None:
    if symptom in SYMPTOM_DISEASE_MAP:
        return symptom

    
    for known in SYMPTOM_DISEASE_MAP.keys():
        if symptom in known or known in symptom:
            return known
    return None


def predict_diseases(symptoms_raw: str):
    raw_items = [part for part in symptoms_raw.split(",") if part.strip()]
    normalized_symptoms = [normalize_symptom(item) for item in raw_items]
    if not normalized_symptoms:
        return []

    disease_weighted_score = defaultdict(float)
    matched_symptom_count = defaultdict(int)
    total_disease_weight = {disease: sum(weights.values()) for disease, weights in DISEASE_SYMPTOM_WEIGHTS.items()}

    for symptom in normalized_symptoms:
        matched_key = match_symptom(symptom)
        if not matched_key:
            continue

        for disease, score in SYMPTOM_DISEASE_MAP[matched_key].items():
            disease_weighted_score[disease] += score
            matched_symptom_count[disease] += 1

    ranked = []
    input_size = len(normalized_symptoms)
    for disease, score_sum in disease_weighted_score.items():
        if matched_symptom_count[disease] == 0:
            continue

        disease_coverage = score_sum / max(total_disease_weight[disease], 1)
        input_match_ratio = matched_symptom_count[disease] / max(input_size, 1)
        confidence = ((disease_coverage * 0.65) + (input_match_ratio * 0.35)) * 100
        ranked.append((disease, round(min(confidence, 99.0), 2)))

    ranked.sort(key=lambda item: item[1], reverse=True)
    return ranked[:3]


@ai_bp.route("/ai", methods=["GET"])
@login_required
def ai_page():
    known_symptoms = sorted(SYMPTOM_DISEASE_MAP.keys())
    return render_template("ai.html", known_symptoms=known_symptoms)


@ai_bp.route("/predict", methods=["POST"])
@login_required
def predict():
    try:
        payload = request.get_json(force=True)
        symptoms = payload.get("symptoms", "")
        predictions = predict_diseases(symptoms)
        if not predictions:
            return jsonify(
                {
                    "message": "No matching disease found. Please enter more common symptoms.",
                    "predictions": [],
                }
            )

        lines = ["Based on your symptoms:"]
        for index, (disease, confidence) in enumerate(predictions, start=1):
            lines.append(f"{index}. {disease.title()} - {confidence:.0f}%")

        return jsonify({"message": "\n".join(lines), "predictions": predictions})
    except Exception as exc:
        print(f"[ERROR] predict failed: {exc}")
        return jsonify({"error": "Prediction failed."}), 500
