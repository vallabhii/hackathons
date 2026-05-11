RESPONSES = {
    "cortisol": "Cortisol is a stress hormone. With PCOS, chronic stress can sometimes make fatigue, cravings, sleep, and cycle symptoms feel louder. Gentle routines, regular meals, light movement, and rest can all be supportive.",
    "insulin": "Insulin resistance means the body has a harder time using insulin efficiently. Balanced meals with fiber, protein, and satisfying carbs can help support steadier energy without restrictive dieting.",
    "stress": "Stress is not a character flaw. Your nervous system may simply need cues of safety: slower breathing, a short walk, warm light, or asking for help.",
    "exercise": "Exercise can support PCOS, but more is not always better. Strength training, walking, yoga, and rest days can all belong in a caring routine.",
    "sleep": "Sleep supports hormones, mood, insulin sensitivity, and cravings. A consistent wind-down routine is often more helpful than chasing a perfect bedtime.",
    "acne": "PCOS acne can be related to androgen shifts, inflammation, or stress. You deserve skincare and medical support without shame or blame.",
    "hair": "Hair loss with PCOS can feel deeply emotional. It may relate to androgens, iron, thyroid, stress, or genetics, so compassionate medical support can be worth seeking.",
    "supplement": "Supplements can help some people, but they are not moral obligations. Inositol, vitamin D, omega-3, or magnesium are commonly discussed, but it is best to check safety with a clinician.",
    "nutrition": "Nutrition for PCOS is about support, not punishment. Think steady meals, enough protein, fiber, color, hydration, and foods you genuinely enjoy.",
    "period": "Irregular periods are common with PCOS. Tracking can help you notice patterns and prepare for care conversations.",
    "fertility": "Many people with PCOS can get pregnant, sometimes with extra support. PCOS can affect ovulation, but it does not erase possibility.",
    "anxiety": "Anxiety can feel consuming. Try naming five things you can see, slowing your exhale, and reminding yourself that this feeling can move through you.",
    "myth": "A common myth is that PCOS is caused by laziness. It is not. PCOS is a hormonal and metabolic condition, and people deserve care without judgment."
}


def answer_question(message):
    text = (message or "").lower()
    for key, response in RESPONSES.items():
        if key in text:
            return response
    return (
        "I can help with PCOS, stress, insulin resistance, sleep, acne, hair loss, periods, fertility, supplements, nutrition, and myths. "
        "Whatever you are carrying today, we can make it feel a little more understandable."
    )
