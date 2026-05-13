const Bloom = {
  email: "",
  user: null,
  today: window.BLOOM_TODAY || "",
  logs: [],
  analytics: null,
  charts: {},
  selectedDate: ""
};

function showToast(message) {
  const toast = document.querySelector("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 3600);
}

function showView(id) {
  document.querySelectorAll(".view").forEach(view => view.classList.remove("active"));
  document.querySelector(`#${id}`).classList.add("active");
}

function showDashboardPage(page = "home") {
  const targetPage = document.querySelector(`#${page}Tab`) ? page : "home";
  document.querySelectorAll(".nav-btn").forEach(item => {
    item.classList.toggle("active", item.dataset.tab === targetPage);
  });
  document.querySelectorAll(".tab").forEach(item => item.classList.remove("active"));
  document.querySelector(`#${targetPage}Tab`).classList.add("active");
  if (targetPage === "analytics") renderCharts();
}
