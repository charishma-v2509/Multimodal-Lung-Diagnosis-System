import joblib
from sentence_transformers import SentenceTransformer

encoder = SentenceTransformer("all-MiniLM-L6-v2")

classifier = joblib.load("models/symptom_severity_model_sklearn161.joblib")
metadata = joblib.load("models/symptom_severity_model_metadata_sklearn161.joblib")


def predict_symptom_severity(symptoms):

    symptoms = symptoms.lower()

    if "shortness of breath" in symptoms or "chest pain" in symptoms:
        severity = "Critical Risk"

    elif "fever" in symptoms or "cough" in symptoms:
        severity = "Moderate Risk"

    else:
        severity = "No Risk"

    return {
        "severity": severity
    }