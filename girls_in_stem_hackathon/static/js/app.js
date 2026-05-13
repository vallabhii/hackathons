async function routeAfterAuth(data) {
  Bloom.user = data.user;
  Bloom.today = data.today;
  if (data.needsOnboarding) {
    showView("onboardingView");
    return;
  }
  if (data.needsCheckin) {
    renderCheckin();
    showView("checkinView");
    return;
  }
  if (!window.location.pathname.startsWith("/dashboard")) {
    history.replaceState({ page: "home" }, "", "/dashboard");
  }
  await loadDashboard();
}

(async function boot() {
  try {
    const data = await api.get("/api/me");
    await routeAfterAuth(data);
  } catch {
    showView("authView");
  }
})();
