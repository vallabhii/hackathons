const Bloom = {
  email: "",
  user: null,
  today: "",
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
