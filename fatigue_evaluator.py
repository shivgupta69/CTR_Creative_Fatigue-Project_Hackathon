def evaluate_fatigue(creative_data):
    peak_ctr = creative_data.get("peak_ctr", 1.5)
    current_ctr = creative_data.get("current_ctr", 0.8)
    ctr_drop_pct = (peak_ctr - current_ctr) / peak_ctr * 100

    days_running = creative_data.get("days_running", 10)
    avg_frequency = creative_data.get("avg_frequency", 3.5)

    hook_time = creative_data.get("hook_time_sec", 3.5)
    text_density = creative_data.get("text_density", "high")
    visual_variation = creative_data.get("visual_variation", "low")

    reasons = []
    recommendations = []
    score = 0

    if ctr_drop_pct >= 40:
        score += 2
        reasons.append("CTR has declined by more than 40%")
        recommendations.append("Refresh ad copy or visuals")

    if avg_frequency >= 3:
        score += 2
        reasons.append("High exposure frequency")
        recommendations.append("Rotate creatives or reduce exposure")

    if hook_time > 2:
        score += 1
        reasons.append("Late hook in the opening seconds")
        recommendations.append("Change the first 2 seconds")

    if text_density == "high":
        score += 1
        reasons.append("Heavy on-screen text")
        recommendations.append("Reduce on-screen text")

    if visual_variation == "low":
        score += 1
        reasons.append("Repetitive visuals")
        recommendations.append("Add scene variation")

    if score >= 5:
        risk = "High"
    elif score >= 3:
        risk = "Medium"
    else:
        risk = "Low"

    return {
        "creative_id": creative_data.get("creative_id", "video_01"),
        "fatigue_risk": risk,
        "reasons": reasons,
        "recommendations": recommendations
    }
