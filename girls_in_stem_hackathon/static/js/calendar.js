function monthDates() {
  const today = new Date();
  const start = new Date(today.getFullYear(), today.getMonth(), 1);
  const end = new Date(today.getFullYear(), today.getMonth() + 1, 0);
  const dates = [];
  for (let day = 1; day <= end.getDate(); day++) {
    dates.push(new Date(start.getFullYear(), start.getMonth(), day).toISOString().slice(0, 10));
  }
  return dates;
}

function renderCalendar() {
  const logsByDate = Object.fromEntries(Bloom.logs.map(log => [log.date, log]));
  const grid = document.querySelector("#calendarGrid");
  grid.innerHTML = monthDates().map(date => {
    const log = logsByDate[date];
    return `<button class="day-card ${log ? "has-log" : ""} ${Bloom.selectedDate === date ? "active" : ""}" data-date="${date}">
      <strong>${new Date(date).getDate()}</strong><br>
      <span>${log ? `${log.mood || "logged"} · ${log.cyclePhase || "cycle"}` : "Add note"}</span>
    </button>`;
  }).join("");
  grid.querySelectorAll(".day-card").forEach(button => button.addEventListener("click", () => openLogEditor(button.dataset.date)));
}

function openLogEditor(date) {
  Bloom.selectedDate = date;
  const log = Bloom.logs.find(item => item.date === date) || {};
  const editor = document.querySelector("#logEditor");
  editor.innerHTML = checkinFields(date, log);
  attachLogForm(editor, () => {
    renderCalendar();
    renderCharts();
    renderInsights();
  });
  renderCalendar();
}
