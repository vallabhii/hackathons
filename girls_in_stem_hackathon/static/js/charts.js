function makeChart(id, label, values, labels, color) {
  if (Bloom.charts[id]) Bloom.charts[id].destroy();
  Bloom.charts[id] = new Chart(document.querySelector(`#${id}`), {
    type: "line",
    data: { labels, datasets: [{ label, data: values, borderColor: color, backgroundColor: `${color}33`, tension: .42, fill: true, pointRadius: 4 }] },
    options: { responsive: true, plugins: { legend: { labels: { color: "#fff1f7" } } }, scales: { x: { ticks: { color: "#dac5e8" }, grid: { color: "rgba(255,255,255,.06)" } }, y: { ticks: { color: "#dac5e8" }, grid: { color: "rgba(255,255,255,.06)" } } }, animation: { duration: 900 } }
  });
}

function renderCharts() {
  if (!Bloom.analytics) return;
  const labels = Bloom.analytics.labels;
  const s = Bloom.analytics.series;
  makeChart("moodChart", "Mood trend", s.mood, labels, "#f29edb");
  makeChart("sleepChart", "Sleep hours", s.sleep, labels, "#a8d8ff");
  makeChart("energyChart", "Energy", s.energy, labels, "#c78bfa");
  if (Bloom.charts.habitChart) Bloom.charts.habitChart.destroy();
  Bloom.charts.habitChart = new Chart(document.querySelector("#habitChart"), {
    type: "bar",
    data: { labels, datasets: [{ label: "Nutrition", data: s.nutrition, backgroundColor: "#ffd6ebaa" }, { label: "Exercise", data: s.exercise, backgroundColor: "#8e6ab8cc" }] },
    options: { responsive: true, plugins: { legend: { labels: { color: "#fff1f7" } } }, scales: { x: { ticks: { color: "#dac5e8" } }, y: { ticks: { color: "#dac5e8" } } } }
  });
}
