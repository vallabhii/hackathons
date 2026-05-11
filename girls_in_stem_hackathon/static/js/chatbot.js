function addBubble(text, who = "bot") {
  const messages = document.querySelector("#chatMessages");
  messages.insertAdjacentHTML("beforeend", `<div class="bubble ${who}">${text}</div>`);
  messages.scrollTop = messages.scrollHeight;
}

document.querySelector("#chatForm").addEventListener("submit", async event => {
  event.preventDefault();
  const input = document.querySelector("#chatInput");
  const message = input.value.trim();
  if (!message) return;
  addBubble(message, "user");
  input.value = "";
  const data = await api.post("/api/chat", { message });
  addBubble(data.reply, "bot");
});
