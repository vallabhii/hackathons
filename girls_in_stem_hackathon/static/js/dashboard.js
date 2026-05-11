const myths = [
  ["You can’t get pregnant with PCOS", "Many people with PCOS can get pregnant, sometimes with ovulation support or medical guidance. PCOS can change the path, but it does not remove hope."],
  ["PCOS only affects overweight people", "PCOS can affect people across body sizes. Symptoms and care needs are real at every size."],
  ["Exercise cures PCOS", "Movement can support insulin sensitivity, mood, and energy, but PCOS is not cured by pushing harder. Rest belongs in care too."],
  ["Losing weight fixes everything", "Weight-focused advice can miss hormones, stress, sleep, genetics, inflammation, and access to care. Bloom centers wellbeing instead."],
  ["PCOS is caused by laziness", "PCOS is a hormonal and metabolic condition. Laziness is not a diagnosis."],
  ["People with PCOS are just undisciplined", "Symptoms like fatigue, cravings, acne, anxiety, and irregular cycles are not moral failures. You deserve support, not judgment."]
];

function renderInsights() {
  const cards = document.querySelector("#insightCards");
  const recs = Bloom.analytics?.recommendations || ["Start with one small act of care today: water, rest, food, light, or a kind message."];
  cards.innerHTML = recs.map((text, index) => `<article class="insight"><h4>Gentle insight ${index + 1}</h4><p>${text}</p></article>`).join("");
}

function renderMyths() {
  document.querySelector("#mythCards").innerHTML = myths.map(([myth, fact]) => `<article class="myth-card"><h4>${myth}</h4><p>${fact}</p></article>`).join("");
}

function renderProfile() {
  const user = Bloom.user || {};
  document.querySelector("#profileCard").innerHTML = `
    <h3>${user.preferredName || "Bloom friend"}</h3>
    <p>${user.email}</p>
    <p><strong>Diagnosis:</strong> ${user.diagnosisStatus || "Not shared"}</p>
    <p><strong>Average cycle:</strong> ${user.averageCycleLength || "Not shared"} days</p>
    <p><strong>Goals:</strong> ${(user.wellnessGoals || []).join(", ") || "Not shared yet"}</p>
    <p class="care-note">All data is securely stored and handled privately.</p>
  `;
}

document.querySelectorAll(".nav-btn").forEach(button => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".nav-btn").forEach(item => item.classList.remove("active"));
    document.querySelectorAll(".tab").forEach(item => item.classList.remove("active"));
    button.classList.add("active");
    document.querySelector(`#${button.dataset.tab}Tab`).classList.add("active");
    if (button.dataset.tab === "analytics") renderCharts();
  });
});

async function refreshLogs() {
  Bloom.logs = (await api.get("/api/logs")).logs;
  Bloom.analytics = await api.get("/api/analytics");
}

async function loadDashboard() {
  await refreshLogs();
  showView("dashboardView");
  const name = Bloom.user?.preferredName || "there";
  document.querySelector("#greeting").textContent = `Hello, ${name}`;
  document.querySelector("#dailyEmpathy").textContent = Bloom.analytics.summary || "Your body is allowed to speak in patterns, pauses, and gentle clues.";
  renderInsights();
  renderCalendar();
  openLogEditor(Bloom.today);
  renderMyths();
  renderProfile();
  renderCharts();
  if (!document.querySelector("#chatMessages").children.length) {
    addBubble("Hi, I’m Bloom. Ask me about PCOS, cortisol, insulin resistance, sleep, nutrition, fertility, or myths. I’ll keep it kind.");
  }
}
