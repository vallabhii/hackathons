const symptoms = ["Irregular periods", "Acne", "Hair changes", "Fatigue", "Cravings", "Cramps", "Bloating", "Anxiety", "Sleep disruption"];
const goals = ["Understand my cycle", "Improve energy", "Support mood", "Lower stress", "Sleep better", "Nourish consistently", "Move gently"];

function renderChoiceChips(containerId, values, name) {
  document.querySelector(containerId).innerHTML = values.map(value => `
    <label class="chip"><input type="checkbox" name="${name}" value="${value}">${value}</label>
  `).join("");
}

renderChoiceChips("#symptomChoices", symptoms, "symptoms");
renderChoiceChips("#goalChoices", goals, "wellnessGoals");

document.querySelector("#onboardingForm").addEventListener("submit", async event => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const payload = Object.fromEntries(form.entries());
  if (payload.lastPeriodDate && payload.lastPeriodDate > Bloom.today) {
    showToast("Date of last period cannot be after today.");
    return;
  }
  payload.symptoms = form.getAll("symptoms");
  payload.wellnessGoals = form.getAll("wellnessGoals");
  try {
    const data = await api.post("/api/onboarding", payload);
    Bloom.user = data.user;
    showToast("Your Bloom space is ready.");
    await loadDashboard();
  } catch (error) {
    showToast(error.message);
  }
});
