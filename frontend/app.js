const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("chatForm");
const messageEl = document.getElementById("message");
const apiKeyEl = document.getElementById("apiKey");
const sessionIdEl = document.getElementById("sessionId");
const statusEl = document.getElementById("status");
const sendBtnEl = document.getElementById("sendBtn");
const clearBtnEl = document.getElementById("clearBtn");
const templateEl = document.getElementById("messageTemplate");

function formatSources(sources) {
  if (!Array.isArray(sources) || sources.length === 0) {
    return [];
  }

  return sources.map((source) => {
    const parts = [];
    if (source.title) parts.push(source.title);
    if (source.page) parts.push(`p.${source.page}`);
    if (source.file) parts.push(source.file);
    return parts.join(" • ");
  });
}

function addMessage(role, content, meta = "", sources = []) {
  const node = templateEl.content.firstElementChild.cloneNode(true);
  node.classList.add(role === "You" ? "user" : "assistant");
  node.querySelector(".role").textContent = role;
  node.querySelector(".meta").textContent = meta;
  node.querySelector(".content").textContent = content;

  const sourceList = node.querySelector(".sources");
  const formattedSources = formatSources(sources);
  if (formattedSources.length === 0) {
    sourceList.remove();
  } else {
    formattedSources.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      sourceList.appendChild(li);
    });
  }

  messagesEl.appendChild(node);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setBusy(isBusy, message) {
  statusEl.textContent = message;
  sendBtnEl.disabled = isBusy;
  messageEl.disabled = isBusy;
}

async function sendMessage(event) {
  event.preventDefault();

  const message = messageEl.value.trim();
  if (!message) return;

  addMessage("You", message, sessionIdEl.value.trim() || "default");
  messageEl.value = "";
  setBusy(true, "Waiting for server...");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": apiKeyEl.value.trim() || "demo_employee_001",
      },
      body: JSON.stringify({
        message,
        session_id: sessionIdEl.value.trim() || "demo-ui-001",
      }),
    });

    const payload = await response.json();

    if (!response.ok || payload.error) {
      const errorMessage = payload?.error?.message || `Request failed with ${response.status}`;
      addMessage("Assistant", errorMessage, payload?.error?.code || "ERROR");
      setBusy(false, "Request failed");
      return;
    }

    addMessage(
      "Assistant",
      payload.answer || "No answer returned.",
      payload.intent || "unknown intent",
      payload.sources || [],
    );
    setBusy(false, "Ready");
  } catch (error) {
    addMessage("Assistant", error.message || "Network error", "NETWORK");
    setBusy(false, "Network error");
  }
}

function clearChat() {
  messagesEl.innerHTML = "";
  statusEl.textContent = "Ready";
  messageEl.focus();
}

formEl.addEventListener("submit", sendMessage);
clearBtnEl.addEventListener("click", clearChat);

addMessage(
  "Assistant",
  "Demo is ready. Try asking about annual leave policy or employee leave status.",
  "welcome",
);
