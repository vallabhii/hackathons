MOOD_SCORE = {"sad": 1, "angry": 2, "anxious": 2, "tired": 2, "neutral": 3, "happy": 5}


def _number(value, fallback=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _linear_regression(values):
    if len(values) < 2:
        return 0
    xs = list(range(len(values)))
    x_mean = sum(xs) / len(xs)
    y_mean = sum(values) / len(values)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, values))
    denominator = sum((x - x_mean) ** 2 for x in xs) or 1
    return round(numerator / denominator, 3)


def build_analytics(logs, user):
    ordered = sorted(logs, key=lambda item: item.get("date", ""))
    labels = [item.get("date") for item in ordered]
    mood = [MOOD_SCORE.get(item.get("mood"), 3) for item in ordered]
    sleep = [_number(item.get("sleep")) for item in ordered]
    energy = [_number(item.get("energy")) for item in ordered]
    nutrition = [_number(item.get("nutrition")) for item in ordered]
    exercise = [_number(item.get("exercise")) for item in ordered]

    recommendations = []
    if sleep and sum(sleep[-5:]) / max(len(sleep[-5:]), 1) < 6 and energy and sum(energy[-5:]) / max(len(energy[-5:]), 1) < 3:
        recommendations.append("Your recent low sleep and low energy may be your body asking for steadier rest. Consider a softer evening routine and gentler movement for a few days.")
    if nutrition and sum(nutrition[-5:]) / max(len(nutrition[-5:]), 1) < 3:
        recommendations.append("Your nutrition check-ins have been low lately. A protein-rich snack or balanced meal can support blood sugar without turning food into a rulebook.")
    if exercise and len([value for value in exercise[-7:] if value >= 4]) >= 5:
        recommendations.append("You have been moving a lot recently. Rest is productive too, especially when stress or fatigue is high.")
    if mood and _linear_regression(mood[-7:]) < -0.2:
        recommendations.append("Your mood trend has been dipping. That is information, not a failure. A check-in with someone safe or a slower day may help.")
    if not recommendations:
        recommendations.append("Your patterns look steady. Keep choosing care that feels realistic, kind, and repeatable.")

    summary = "Bloom noticed your recent patterns and translated them into gentle, practical next steps."
    return {
        "labels": labels,
        "series": {
            "mood": mood,
            "sleep": sleep,
            "energy": energy,
            "nutrition": nutrition,
            "exercise": exercise
        },
        "trends": {
            "mood": _linear_regression(mood),
            "sleep": _linear_regression(sleep),
            "energy": _linear_regression(energy),
            "nutrition": _linear_regression(nutrition),
            "exercise": _linear_regression(exercise)
        },
        "summary": summary,
        "recommendations": recommendations,
        "preferredName": user.get("preferredName") if user else ""
    }
