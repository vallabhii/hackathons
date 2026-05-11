const moodMessages = {
  anxious: "Anxiety can feel loud. Bloom is here with a softer pace and no pressure to perform.",
  sad: "Sadness deserves room. Thank you for being honest with yourself today.",
  happy: "It is lovely to see a bright note today. Let it be real without needing to be perfect.",
  angry: "Anger often carries a need or boundary. You are allowed to listen to it gently.",
  tired: "Tired counts. Rest and slower choices are valid care.",
  neutral: "Neutral days matter too. You do not need a dramatic feeling for your check-in to count."
};

function checkinFields(dateKey = Bloom.today, log = {}) {
  return `
    <label>Mood<select name="mood">${["happy","sad","anxious","angry","tired","neutral"].map(v => `<option ${log.mood === v ? "selected" : ""}>${v}</option>`).join("")}</select></label>
    <label>Energy level<select name="energy">${[1,2,3,4,5].map(v => `<option value="${v}" ${String(log.energy) === String(v) ? "selected" : ""}>${v}</option>`).join("")}</select></label>
    <label>Sleep hours<input name="sleep" type="number" min="0" max="14" step=".5" value="${log.sleep || ""}"></label>
    <label>Nutrition<select name="nutrition">${[1,2,3,4,5].map(v => `<option value="${v}" ${String(log.nutrition) === String(v) ? "selected" : ""}>${v}</option>`).join("")}</select></label>
    <label>Exercise<select name="exercise">${[0,1,2,3,4,5].map(v => `<option value="${v}" ${String(log.exercise) === String(v) ? "selected" : ""}>${v}</option>`).join("")}</select></label>
    <label>Symptoms<input name="symptoms" placeholder="cramps, acne, fatigue..." value="${(log.symptoms || []).join(", ")}"></label>
    <label>Cycle phase<input name="cyclePhase" placeholder="menstrual, follicular, ovulatory..." value="${log.cyclePhase || ""}"></label>
    <label>Date<input name="date" type="date" value="${dateKey}"></label>
    <label class="wide">Notes<textarea name="notes" placeholder="Anything your body or heart wants noted?">${log.notes || ""}</textarea></label>
    <button class="primary-btn wide" type="submit">Save check-in</button>
  `;
}

function attachLogForm(form, afterSave) {
  form.addEventListener("submit", async event => {
    event.preventDefault();
    const values = Object.fromEntries(new FormData(form).entries());
    const date = values.date || Bloom.today;
    values.symptoms = values.symptoms ? values.symptoms.split(",").map(item => item.trim()).filter(Boolean) : [];
    const data = await api.post(`/api/logs/${date}`, values);
    Bloom.analytics = data.analytics;
    showToast(moodMessages[values.mood] || "Saved with care.");
    await refreshLogs();
    if (afterSave) afterSave();
  });
}

function renderCheckin() {
  const form = document.querySelector("#checkinForm");
  form.innerHTML = checkinFields(Bloom.today);
  attachLogForm(form, loadDashboard);
}
