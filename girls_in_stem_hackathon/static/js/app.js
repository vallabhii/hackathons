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
