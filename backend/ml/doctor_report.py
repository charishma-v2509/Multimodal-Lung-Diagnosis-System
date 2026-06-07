"""
Doctor Report Generator

Provides detailed clinical analysis
based on multimodal AI predictions.
"""


def generate_modality_contribution(
    image_result,
    text_result,
    vitals_result,
    symptom_severity
):
    """
    Explains which modality contributed to the diagnosis.
    """

    contribution = {}

    if image_result != "Normal":
        contribution["image_model"] = "Abnormal lung patterns detected in chest X-ray"
    else:
        contribution["image_model"] = "No significant abnormalities detected"

    if text_result != "Normal":
        contribution["text_model"] = "Clinical notes suggest possible respiratory condition"
    else:
        contribution["text_model"] = "No concerning clinical indicators in notes"

    if vitals_result != "Normal":
        contribution["vitals_model"] = "Vital signs indicate respiratory stress"
    else:
        contribution["vitals_model"] = "Vital signs within acceptable range"

    if symptom_severity not in ["No Risk", "Low Risk"]:
        contribution["symptom_model"] = "Reported symptoms indicate possible illness"
    else:
        contribution["symptom_model"] = "Symptoms indicate low risk"

    return contribution

def generate_differential_diagnosis(
    image_result,
    text_result,
    vitals_result,
    symptom_severity,
    final_result,
    image_probabilities=None
):
    """
    Generates possible alternative diagnoses
    based on multimodal signals and image model probabilities.
    """
    diagnoses = []

    # If we have actual image probabilities, use them to build the list
    if image_probabilities:
        # Sort probabilities and take top 4
        sorted_probs = sorted(
            image_probabilities.items(), 
            key=lambda item: item[1], 
            reverse=True
        )
        
        for condition, prob in sorted_probs:
            # Skip "No Finding" as a differential diagnosis item
            if condition == "No Finding":
                continue
            
            # Convert to percentage
            percent = int(prob * 100)
            if percent > 5: # Only include if > 5% confidence
                diagnoses.append({
                    "condition": condition,
                    "confidence": percent
                })
                
        # Limit to top 5
        diagnoses = diagnoses[:5]

    # Fallback if no image probabilities or list is empty
    if not diagnoses:
        if final_result != "Normal":
            diagnoses.append({"condition": "Pneumonia", "confidence": 85})
            diagnoses.append({"condition": "Atelectasis", "confidence": 45})
        else:
            diagnoses.append({"condition": "No significant respiratory condition suspected", "confidence": 100})

    return diagnoses

def generate_clinical_red_flags(
    vitals_result,
    symptom_severity
):
    """
    Identifies critical warning indicators from vitals and symptoms.
    """

    red_flags = []

    if vitals_result != "Normal":
        red_flags.append("Abnormal vital signs indicating possible respiratory distress")

    if symptom_severity in ["High Risk", "Severe"]:
        red_flags.append("Severe respiratory symptoms reported")

    if symptom_severity in ["Moderate", "High Risk"]:
        red_flags.append("Symptoms may indicate an active respiratory infection")

    if not red_flags:
        red_flags.append("No critical clinical red flags detected")

    return red_flags


def generate_suggested_tests(
    image_result,
    vitals_result,
    symptom_severity
):
    """
    Suggests follow-up diagnostic tests
    based on detected abnormalities.
    """

    tests = []

    if image_result != "Normal":
        tests.append("Chest CT scan for detailed lung imaging")

    if vitals_result != "Normal":
        tests.append("Arterial blood gas analysis")

    if symptom_severity not in ["No Risk", "Low Risk"]:
        tests.append("Complete blood count (CBC)")
        tests.append("C-reactive protein (CRP) test")

    if not tests:
        tests.append("Routine clinical observation")

    return tests


def generate_confidence_calibration(
    image_result,
    text_result,
    vitals_result,
    symptom_severity,
    final_result
):
    """
    Estimates model confidence based on agreement
    between multiple modalities.
    """

    abnormal_count = 0

    if image_result != "Normal":
        abnormal_count += 1

    if text_result != "Normal":
        abnormal_count += 1

    if vitals_result != "Normal":
        abnormal_count += 1

    if symptom_severity not in ["No Risk", "Low Risk"]:
        abnormal_count += 1

    if abnormal_count >= 3:
        return "High Confidence"

    if abnormal_count == 2:
        return "Moderate Confidence"

    if abnormal_count <= 1:
        return "Low Confidence"

    return "Moderate Confidence"


def generate_multimodal_explanation_score(
    image_result,
    text_result,
    vitals_result,
    symptom_severity
):
    """
    Computes approximate contribution percentages
    from each modality based on abnormal findings.
    """

    contributions = {
        "image_model": 0,
        "text_model": 0,
        "vitals_model": 0,
        "symptom_model": 0
    }

    active_modalities = []

    if image_result != "Normal":
        active_modalities.append("image_model")

    if text_result != "Normal":
        active_modalities.append("text_model")

    if vitals_result != "Normal":
        active_modalities.append("vitals_model")

    if symptom_severity not in ["No Risk", "Low Risk"]:
        active_modalities.append("symptom_model")

    if not active_modalities:
        return contributions

    share = int(100 / len(active_modalities))

    for m in active_modalities:
        contributions[m] = share

    return contributions


def generate_doctor_report(
    image_result,
    text_result,
    vitals_result,
    symptom_severity,
    final_result,
    heatmap_path=None,
    image_probabilities=None
):

    modality_contribution = {
        "image_model": image_result,
        "text_model": text_result,
        "vitals_model": vitals_result,
        "symptom_model": symptom_severity
    }

    differential_diagnosis = generate_differential_diagnosis(
        image_result, text_result, vitals_result, symptom_severity, final_result, image_probabilities
    )

    red_flags = []

    if vitals_result == "Abnormal":
        red_flags.append("Abnormal vital signs")

    if symptom_severity == "Critical Risk":
        red_flags.append("Severe respiratory symptoms")

    return {
        "final_prediction": final_result,
        "modality_contribution": modality_contribution,
        "differential_diagnosis": differential_diagnosis,
        "clinical_red_flags": red_flags,
        "heatmap_path": heatmap_path
    }