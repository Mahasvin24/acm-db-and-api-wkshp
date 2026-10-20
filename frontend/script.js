const conversationList = document.querySelector("#conversation-list");
const chatTitle = document.querySelector("#chat-title");
const chatArea = document.querySelector("#chat-area");
const emptyState = document.querySelector("#empty-state");
const messages = document.querySelector("#messages");
const form = document.querySelector("#message-form");
const input = document.querySelector("#message-input");
const sendButton = document.querySelector("#send");
const errorBox = document.querySelector("#error");
const statusNote = document.querySelector("#status");

let conversationId = -1;
let busy = false;
const defaultStatus = "Local AI · Your conversations are saved on this computer.";

async function api(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = body.detail;
    const error = new Error(typeof detail === "string"
      ? detail : detail?.message || `Request failed (${response.status}).`);
    error.conversationId = detail?.conversation_id;
    throw error;
  }
  return response.json();
}

function showError(message = "") {
  errorBox.textContent = message;
  errorBox.hidden = !message;
}

function setBusy(value) {
  busy = value;
  document.querySelectorAll("button").forEach((button) => { button.disabled = value; });
  input.disabled = value;
  sendButton.disabled = value || !input.value.trim();
  chatArea.setAttribute("aria-busy", String(value));
  statusNote.textContent = value ? "Loading…" : defaultStatus;
}

function markActiveConversation() {
  conversationList.querySelectorAll("button").forEach((button) => {
    button.setAttribute("aria-current", String(Number(button.dataset.id) === conversationId));
  });
}

async function loadConversations() {
  const conversations = await api("/conversations");
  conversationList.replaceChildren();
  if (conversations.length === 0) {
    const note = document.createElement("p");
    note.className = "history-empty";
    note.textContent = "Your first conversation starts here.";
    conversationList.append(note);
  }
  conversations.slice().reverse().forEach((conversation) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "conversation";
    button.dataset.id = conversation.id;
    button.disabled = busy;
    const name = document.createElement("span");
    name.className = "conversation-name";
    name.textContent = `Conversation ${conversation.id}`;
    const date = document.createElement("span");
    date.className = "conversation-date";
    const timestamp = new Date(conversation.created_at.replace(" ", "T") + "Z");
    date.textContent = timestamp.toLocaleDateString(undefined, { month: "short", day: "numeric" });
    button.append(name, date);
    button.addEventListener("click", () => selectConversation(conversation.id));
    conversationList.append(button);
  });
  markActiveConversation();
}

async function loadMessages(id) {
  const history = await api(`/conversations/${id}/messages`);
  conversationId = id;
  chatTitle.textContent = `Conversation ${id}`;
  emptyState.hidden = history.length > 0;
  messages.replaceChildren();
  history.forEach((message) => {
    const article = document.createElement("article");
    article.className = message.role === "user" ? "message user" : "message";
    const label = document.createElement("div");
    label.className = "message-label";
    label.textContent = message.role === "user" ? "You" : message.role;
    const content = document.createElement("div");
    content.className = "message-content";
    content.textContent = message.content;
    article.append(label, content);
    messages.append(article);
  });
  markActiveConversation();
  chatArea.scrollTop = chatArea.scrollHeight;
}

async function selectConversation(id) {
  if (busy) return;
  showError();
  setBusy(true);
  try {
    await loadMessages(id);
  } catch (error) {
    showError(`Couldn't load this conversation. ${error.message}`);
  } finally {
    setBusy(false);
    input.focus();
  }
}

document.querySelector("#new-chat").addEventListener("click", () => {
  if (busy) return;
  conversationId = -1;
  chatTitle.textContent = "New conversation";
  messages.replaceChildren();
  emptyState.hidden = false;
  markActiveConversation();
  showError();
  input.value = "";
  sendButton.disabled = true;
  chatArea.scrollTop = 0;
  input.focus();
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.dataset.prompt;
    sendButton.disabled = busy;
    input.focus();
  });
});

input.addEventListener("input", () => { sendButton.disabled = busy || !input.value.trim(); });
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    if (!busy && input.value.trim()) form.requestSubmit();
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const content = input.value.trim();
  if (busy || !content) return;
  showError();
  setBusy(true);
  statusNote.textContent = "Waiting for a reply…";
  let saved = false;
  try {
    const result = await api("/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conv_id: conversationId, role: "user", content }),
    });
    saved = true;
    conversationId = result.conversation_id;
    input.value = "";
    await loadMessages(conversationId);
    await loadConversations();
  } catch (error) {
    if (error.conversationId !== undefined) {
      conversationId = error.conversationId;
      input.value = "";
      try {
        await loadMessages(conversationId);
        await loadConversations();
        showError(`${error.message} Your message was saved. Once fixed, send another message to continue.`);
      } catch {
        showError(`${error.message} Your message was saved. Reload to view your history.`);
      }
    } else {
      showError(saved
        ? "Your message was saved, but history couldn't refresh. Reload the page to try again."
        : `Couldn't send your message. ${error.message}`);
    }
  } finally {
    setBusy(false);
    input.focus();
  }
});

async function start() {
  setBusy(true);
  try {
    await loadConversations();
  } catch (error) {
    showError(`Couldn't load your history. Check that the API is running, then reload. ${error.message}`);
  } finally {
    setBusy(false);
  }
}

start();
