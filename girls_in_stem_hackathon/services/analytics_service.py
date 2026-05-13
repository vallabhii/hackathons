MOOD_SCORE = {"sad": 1, "angry": 2, "anxious": 2, "tired": 2, "neutral": 3, "happy": 5}
ENERGY_INPUTS = {
    "sleep": "sleep hours",
    "proteinGrams": "protein",
    "fatGrams": "fat",
    "calories": "calories",
    "exerciseHours": "exercise"
}


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


def _regression_slope(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 2:
        return 0
    x_values = [item[0] for item in pairs]
    y_values = [item[1] for item in pairs]
    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(y_values) / len(y_values)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in pairs)
    denominator = sum((x - x_mean) ** 2 for x in x_values) or 1
    return round(numerator / denominator, 3)


def _average(values):
    values = [value for value in values if value is not None]
    return round(sum(values) / len(values), 1) if values else 0


def _format_amount(key, value):
    if key == "sleep":
        return f"{value:g} hours of sleep"
    if key == "exerciseHours":
        return f"{value:g} hours of exercise"
    if key == "calories":
        return f"{value:g} calories"
    if key == "proteinGrams":
        return f"{value:g}g protein"
    if key == "fatGrams":
        return f"{value:g}g fat"
    return str(value)


def _series(ordered, key, fallback_key=None):
    return [
        _number(item.get(key, item.get(fallback_key) if fallback_key else None))
        for item in ordered
    ]


def _relationship_series(ordered, key, fallback_key=None):
    return [
        _number(item.get(key, item.get(fallback_key) if fallback_key else None), None)
        for item in ordered
    ]


def build_analytics(logs, user):
    ordered = sorted(logs, key=lambda item: item.get("date", ""))
    labels = [item.get("date") for item in ordered]
    mood = [MOOD_SCORE.get(item.get("mood"), 3) for item in ordered]
    sleep = _series(ordered, "sleep")
    energy = [_number(item.get("energy")) for item in ordered]
    exercise_hours = _series(ordered, "exerciseHours", "exercise")
    calories = _series(ordered, "calories")
    protein_grams = _series(ordered, "proteinGrams")
    fat_grams = _series(ordered, "fatGrams")

    energy_inputs = {
        "sleep": _relationship_series(ordered, "sleep"),
        "proteinGrams": _relationship_series(ordered, "proteinGrams"),
        "fatGrams": _relationship_series(ordered, "fatGrams"),
        "calories": _relationship_series(ordered, "calories"),
        "exerciseHours": _relationship_series(ordered, "exerciseHours", "exercise")
    }
    energy_relationships = {
        key: _regression_slope(values, energy)
        for key, values in energy_inputs.items()
    }

    highest_energy = max(energy) if energy else 0
    best_energy_logs = [
        item for item in ordered
        if _number(item.get("energy")) == highest_energy and highest_energy > 0
    ]
    best_day_averages = {
        key: _average([
            _number(item.get(key, item.get("exercise") if key == "exerciseHours" else None), None)
            for item in best_energy_logs
        ])
        for key in ENERGY_INPUTS
    }

    recommendations = []
    if sleep and sum(sleep[-5:]) / max(len(sleep[-5:]), 1) < 6 and energy and sum(energy[-5:]) / max(len(energy[-5:]), 1) < 3:
        recommendations.append("Your recent low sleep and low energy may be your body asking for steadier rest. Consider a softer evening routine and gentler movement for a few days.")
    if exercise_hours and len([value for value in exercise_hours[-7:] if value >= 2]) >= 5:
        recommendations.append("You have been moving a lot recently. Rest is productive too, especially when stress or fatigue is high.")
    if mood and _linear_regression(mood[-7:]) < -0.2:
        recommendations.append("Your mood trend has been dipping. That is information, not a failure. A check-in with someone safe or a slower day may help.")
    if best_energy_logs:
        strongest_inputs = sorted(
            energy_relationships,
            key=lambda key: energy_relationships[key],
            reverse=True
        )[:3]
        repeatable_patterns = [
            _format_amount(key, best_day_averages[key])
            for key in strongest_inputs
            if best_day_averages[key] and energy_relationships[key] >= 0
        ]
        if repeatable_patterns:
            recommendations.append(
                "Your best-energy days tended to include "
                + ", ".join(repeatable_patterns)
                + ". Try repeating one of those patterns this week and see how your energy responds."
            )
    if not recommendations:
        recommendations.append("Your patterns look steady. Keep choosing care that feels realistic, kind, and repeatable.")

    summary = "Bloom noticed your recent patterns and translated them into gentle, practical next steps."
    return {
        "labels": labels,
        "series": {
            "mood": mood,
            "sleep": sleep,
            "energy": energy,
            "exerciseHours": exercise_hours,
            "calories": calories,
            "proteinGrams": protein_grams,
            "fatGrams": fat_grams
        },
        "trends": {
            "mood": _linear_regression(mood),
            "sleep": _linear_regression(sleep),
            "energy": _linear_regression(energy),
            "exerciseHours": _linear_regression(exercise_hours),
            "calories": _linear_regression(calories),
            "proteinGrams": _linear_regression(protein_grams),
            "fatGrams": _linear_regression(fat_grams)
        },
        "energyRelationships": energy_relationships,
        "bestEnergyAverages": best_day_averages,
        "summary": summary,
        "recommendations": recommendations,
        "preferredName": user.get("preferredName") if user else ""
    }
