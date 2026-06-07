# ==============================================
# MULTIMODAL LATE FUSION ENGINE
# ==============================================

IMAGE_WEIGHT = 0.30
TEXT_WEIGHT = 0.25
VITALS_WEIGHT = 0.30
SYMPTOM_WEIGHT = 0.15


# ----------------------------------------------
# SCORE MAPPINGS
# ----------------------------------------------

TEXT_MAP = {
    "Normal": 0.1,
    "Abnormal": 0.8
}

VITALS_MAP = {
    "Normal": 0.2,
    "Abnormal": 0.7
}

SYMPTOM_MAP = {
    "No Risk": 0.1,
    "Moderate Risk": 0.6,
    "Critical Risk": 1.0
}


# ----------------------------------------------
# LATE FUSION FUNCTION
# ----------------------------------------------

def fusion_decision(
    image_output,
    text_result,
    vitals_result,
    symptom_severity
):

    # Image probability from model
    image_score = image_output["fusion_probability"]

    # Convert other modalities
    text_score = TEXT_MAP.get(text_result, 0.1)
    vitals_score = VITALS_MAP.get(vitals_result, 0.2)
    symptom_score = SYMPTOM_MAP.get(symptom_severity, 0.1)

    # ----------------------------------------------
    # Late fusion calculation
    # ----------------------------------------------

    fusion_score = (
        IMAGE_WEIGHT * image_score +
        TEXT_WEIGHT * text_score +
        VITALS_WEIGHT * vitals_score +
        SYMPTOM_WEIGHT * symptom_score
    )

    # ----------------------------------------------
    # Final clinical decision
    # ----------------------------------------------

    # ----------------------------------------------
    # CLINICAL SAFETY OVERRIDE
    # ----------------------------------------------

    if vitals_result == "Abnormal" and symptom_severity == "Critical Risk":
        final_result = "Lung Disease Detected"

    # ----------------------------------------------
    # NORMAL FUSION DECISION
    # ----------------------------------------------

    elif fusion_score >= 0.5:
        final_result = "Lung Disease Detected"

    else:
        final_result = "Normal"

    return {
        "final_prediction": final_result,
        "fusion_score": round(fusion_score, 3),
        "modality_scores": {
            "image_probability": round(image_score, 3),
            "text_score": text_score,
            "vitals_score": vitals_score,
            "symptom_score": symptom_score
        }
    }