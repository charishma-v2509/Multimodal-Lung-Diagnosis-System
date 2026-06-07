def analyze_vitals(oxygen, heart_rate, temperature, respiratory_rate):

    score = 0

    if oxygen < 94:
        score += 2

    if heart_rate > 100:
        score += 1

    if temperature > 38:
        score += 1

    if respiratory_rate > 22:
        score += 2

    if score >= 3:
        result = "Abnormal"
    else:
        result = "Normal"

    return {
        "vitals_result": result,
        "vitals_score": score
    }