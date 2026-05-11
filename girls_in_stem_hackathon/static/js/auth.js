let authIntent = "login";

document.querySelectorAll("#authForm button").forEach(button => {
  button.addEventListener("click", () => authIntent = button.dataset.intent);
});

document.querySelector("#authForm").addEventListener("submit", async event => {
  event.preventDefault();
  Bloom.email = document.querySelector("#emailInput").value.trim().toLowerCase();
  try {
    const data = await api.post("/api/auth/request-otp", { email: Bloom.email, intent: authIntent });
    document.querySelector("#authMessage").textContent = data.devOtp ? `${data.message} OTP: ${data.devOtp}` : data.message;
    document.querySelector("#otpForm").classList.remove("hidden");
  } catch (error) {
    document.querySelector("#authMessage").textContent = error.message;
    showToast(error.message);
  }
});

document.querySelector("#otpForm").addEventListener("submit", async event => {
  event.preventDefault();
  try {
    const data = await api.post("/api/auth/verify-otp", {
      email: Bloom.email,
      otp: document.querySelector("#otpInput").value.trim()
    });
    await routeAfterAuth(data);
  } catch (error) {
    showToast(error.message);
  }
});

document.querySelector("#logoutBtn").addEventListener("click", async () => {
  await api.post("/api/auth/logout", {});
  location.reload();
});
