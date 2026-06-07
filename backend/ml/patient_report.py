"""
Patient Report Generator

This module converts raw model outputs into
patient-friendly health insights.
"""
def generate_health_risk_summary(
    image_result,
    text_result,
    vitals_result,
    symptom_severity,
    final_result
):
    """
    Determines overall patient health risk level
    based on multimodal model outputs.
    """

    if final_result == "Normal":
        return "Low Risk"

    if symptom_severity in ["Low Risk", "Mild"]:
        return "Moderate Risk"

    if vitals_result == "Disease":
        return "High Risk"

    if symptom_severity in ["High Risk", "Severe"]:
        return "Critical Risk"

    return "Moderate Risk"

def generate_condition_explanation(
    image_result,
    text_result,
    vitals_result,
    symptom_severity,
    final_result
):
    """
    Builds a simple explanation for patients describing
    why the system suspects a condition.
    """

    reasons = []

    if image_result != "Normal":
        reasons.append(
            "patterns detected in the chest X-ray that may indicate lung abnormalities"
        )

    if text_result != "Normal":
        reasons.append(
            "clinical notes suggesting possible respiratory issues"
        )

    if vitals_result != "Normal":
        reasons.append(
            "vital signs showing abnormal respiratory indicators"
        )

    if symptom_severity not in ["No Risk", "Low Risk"]:
        reasons.append(
            "reported symptoms such as cough, fever, or breathing difficulty"
        )

    if not reasons:
        return "No significant abnormalities were detected in the available data."

    explanation = "The AI system detected " + ", ".join(reasons) + "."
    explanation += " These findings may be associated with a respiratory condition."

    return explanation


def determine_urgency(
    vitals_result,
    symptom_severity,
    final_result
):
    """
    Determines how urgently the patient should seek care.
    """

    if final_result == "Normal" and symptom_severity in ["No Risk", "Low Risk"]:
        return "Normal"

    if symptom_severity in ["Low Risk", "Mild"]:
        return "Monitor"

    if vitals_result != "Normal":
        return "Serious"

    if symptom_severity in ["High Risk", "Severe"]:
        return "Immediate Care"

    return "Monitor"


def generate_recommendations(urgency_level):
    """
    Provides recommended next steps for the patient
    based on the urgency level.
    """

    if urgency_level == "Normal":
        return (
            "No immediate health concerns were detected. Maintain a healthy lifestyle, "
            "stay hydrated, exercise regularly, and monitor your health periodically."
        )

    if urgency_level == "Monitor":
        return (
            "Some mild indicators were detected. Monitor your symptoms, ensure adequate rest, "
            "stay hydrated, and consult a healthcare professional if symptoms persist or worsen."
        )

    if urgency_level == "Serious":
        return (
            "Several indicators suggest a possible respiratory condition. It is recommended "
            "to schedule a consultation with a healthcare professional soon for further evaluation."
        )

    if urgency_level == "Immediate Care":
        return (
            "Critical health indicators were detected. Seek immediate medical attention or "
            "visit the nearest healthcare facility as soon as possible."
        )

    return "Please consult a healthcare professional for further evaluation."

def generate_patient_report(
    image_result,
    text_result,
    vitals_result,
    symptom_severity,
    final_result
):

    if final_result == "Normal":
        risk = "Low Risk"
        urgency = "Normal"
        explanation = "No major abnormalities were detected across the analyzed medical data."
        next_steps = "Maintain a healthy lifestyle and monitor symptoms if they persist."

    else:
        risk = "Moderate Risk"
        urgency = "Medical Attention Recommended"
        explanation = (
            "The AI system detected patterns across medical data that may indicate a lung-related condition."
        )
        next_steps = "Consult a healthcare professional for further evaluation."

    modality_contribution = {
        "image_model": image_result,
        "text_model": text_result,
        "vitals_model": vitals_result,
        "symptom_model": symptom_severity
    }

    red_flags = []
    if vitals_result == "Abnormal":
        red_flags.append("Abnormal vital signs")
    if symptom_severity == "Critical Risk":
        red_flags.append("Severe respiratory symptoms")

    return {
        "health_risk_summary": risk,
        "possible_condition_explanation": explanation,
        "urgency_indicator": urgency,
        "recommended_next_steps": next_steps,
        "modality_contribution": modality_contribution,
        "clinical_red_flags": red_flags,
        "disclaimer": "This AI system provides preliminary insights and does not replace professional medical diagnosis."
    }