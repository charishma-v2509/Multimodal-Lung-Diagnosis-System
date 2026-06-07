
IMAGE_WEIGHT = 0.5
TEXT_WEIGHT = 0.3
VITALS_WEIGHT = 0.2

VITALS_SCORE_MAP = {
    "LOW": 0.3,
    "MEDIUM": 0.6,
    "HIGH": 1.0
}

HIGH_THRESHOLD = 0.75
MEDIUM_THRESHOLD = 0.5


def fusion_decision(
    image_class,
    image_conf,
    text_abnormal,
    text_conf,
    vitals_risk
):

    if text_abnormal:
        text_score = text_conf
    else:
        text_score = 0.2

    vitals_score = VITALS_SCORE_MAP.get(vitals_risk, 0.3)

    final_score = (
        (IMAGE_WEIGHT * image_conf)
        + (TEXT_WEIGHT * text_score)
        + (VITALS_WEIGHT * vitals_score)
    )

    if final_score >= HIGH_THRESHOLD:
        risk_level = "HIGH"
        recommendation = "Immediate clinical review advised."
    elif final_score >= MEDIUM_THRESHOLD:
        risk_level = "MEDIUM"
        recommendation = "Doctor consultation recommended."
    else:
        risk_level = "LOW"
        recommendation = "Monitor symptoms and follow precautions."

    result = {
        "risk_level": risk_level,
        "primary_prediction": image_class,
        "confidence": round(image_conf, 3),
        "final_score": round(final_score, 3),
        "recommendation": recommendation,
        "source_breakdown": {
            "image": {
                "class": image_class,
                "confidence": round(image_conf, 3)
            },
            "text": {
                "abnormal": text_abnormal,
                "confidence": round(text_conf, 3)
            },
            "vitals": {
                "risk": vitals_risk,
                "score": vitals_score
            }
        }
    }

    return result
