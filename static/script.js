/* ===============================
   AI Chat - frontend logic
   =============================== */

let currentSessionId = null;
let selectedSessionId = null;
let renameInputEl = null;
let archivedView = false;

/* ---------- Helpers ---------- */

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str == null ? "" : String(str);
    return div.innerHTML;
}

function isJson(value) {
    try {
        JSON.parse(value);
        return true;
    } catch (e) {
        return false;
    }
}

function scrollToBottom() {
    const scroller = document.querySelector(".chat-scroll");
    if (scroller) scroller.scrollTop = scroller.scrollHeight;
}

/* ---------- Markdown + code rendering ---------- */

function renderMarkdown(text) {
    if (window.marked && typeof marked.parse === "function") {
        return marked.parse(text || "");
    }
    return escapeHtml(text).replace(/\n/g, "<br>");
}

function highlightCode(root) {
    if (window.hljs) {
        root.querySelectorAll("pre code").forEach(function (block) {
            try {
                hljs.highlightElement(block);
            } catch (e) {
                /* ignore highlight failures */
            }
        });
    }
}

function attachCopyButtons(root) {
    root.querySelectorAll("pre").forEach(function (pre) {
        const code = pre.querySelector("code");
        if (!code) return;

        // Avoid adding duplicate buttons after re-render during streaming.
        if (pre.querySelector(".copy-code-btn")) return;

        const btn = document.createElement("button");
        btn.className = "copy-code-btn";
        btn.type = "button";
        btn.innerText = "Copy code";

        btn.addEventListener("click", async function () {
            try {
                await navigator.clipboard.writeText(code.innerText.trim());
                btn.innerText = "Copied!";
                btn.classList.add("copied");
                setTimeout(function () {
                    btn.innerText = "Copy code";
                    btn.classList.remove("copied");
                }, 2000);
            } catch (e) {
                btn.innerText = "Copy failed";
            }
        });

        pre.appendChild(btn);
    });
}

/* ---------- Message building ---------- */

function buildUserRow(text) {
    const row = document.createElement("div");
    row.className = "message-row user";

    const content = document.createElement("div");
    content.className = "message-content";
    content.textContent = text;

    const avatar = document.createElement("div");
    avatar.className = "avatar user";
    avatar.innerText = "🧑";

    row.append(content, avatar);
    return row;
}

function buildBotRow(text) {
    const row = document.createElement("div");
    row.className = "message-row bot";

    const avatar = document.createElement("div");
    avatar.className = "avatar bot";
    avatar.innerText = "🤖";

    const content = document.createElement("div");
    content.className = "message-content";
    const md = document.createElement("div");
    md.className = "md-body";
    md.innerHTML = renderMarkdown(text);
    highlightCode(md);
    attachCopyButtons(md);

    content.appendChild(md);
    row.append(avatar, content);
    return row;
}

/* ---------- Send / streaming ---------- */

async function sendMessage() {
    const input = document.getElementById("message");
    const message = input.value.trim();
    if (!message) return;

    const sendBtn = document.getElementById("sendBtn");
    const chatBox = document.getElementById("chatbox");
    const chatTitle = document.getElementById("chatTitle");

    sendBtn.disabled = true;
    input.disabled = true;
    input.value = "";

    if (chatTitle) {
        chatTitle.innerText =
            message.length > 30 ? message.slice(0, 30) + "…" : message;
    }

    chatBox.appendChild(buildUserRow(message));

    // Empty bot row filled as tokens stream in.
    const botRow = document.createElement("div");
    botRow.className = "message-row bot typing";
    const botAvatar = document.createElement("div");
    botAvatar.className = "avatar bot";
    botAvatar.innerText = "🤖";
    const botContent = document.createElement("div");
    botContent.className = "message-content";
    const mdBody = document.createElement("div");
    mdBody.className = "md-body";
    botContent.appendChild(mdBody);
    botRow.append(botAvatar, botContent);
    chatBox.appendChild(botRow);
    scrollToBottom();

    let fullResponse = "";

    try {
        const response = await fetch("/chat-stream", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                messages: [{ role: "user", content: message }]
            })
        });

        if (!response.ok || !response.body) {
            throw new Error("Request failed with status " + response.status);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            fullResponse += decoder.decode(value, { stream: true });
            mdBody.innerHTML = renderMarkdown(fullResponse);
            highlightCode(mdBody);
            attachCopyButtons(mdBody);
            scrollToBottom();
        }
    } catch (err) {
        mdBody.innerHTML = escapeHtml("[Error: " + err.message + "]");
    }

    botRow.classList.remove("typing");
    sendBtn.disabled = false;
    input.disabled = false;
    input.focus();
    scrollToBottom();

    // Refresh the session list so the new/updated chat appears.
    loadSessions();
}

/* ---------- Session list ---------- */

function getSessionDisplayName(session) {
    let label = session[1];
    if (isJson(label)) {
        try {
            const jsonData = JSON.parse(label);
            if (Array.isArray(jsonData) && jsonData.length && jsonData[0].content) {
                label = jsonData[0].content;
            }
        } catch (e) { /* keep original label */ }
    }
    return (label && String(label).trim()) ? String(label) : "Untitled";
}

function loadSessions() {
    fetch("/sessions")
        .then(response => response.json())
        .then(sessions => {
            renderSessionList(sessions);
        })
        .catch(err => console.error("loadSessions error:", err));
}

function loadArchivedSessions() {
    fetch("/archived-chats")
        .then(response => response.json())
        .then(sessions => {
            renderSessionList(sessions);
        })
        .catch(err => console.error("loadArchivedSessions error:", err));
}

function renderSessionList(sessions) {
    const sidebar = document.getElementById("sessions");
    sidebar.innerHTML = "";

    if (!sessions || sessions.length === 0) {
        const empty = document.createElement("div");
        empty.className = "session-empty";
        empty.innerText = archivedView ? "No archived chats" : "No chats yet";
        sidebar.appendChild(empty);
        return;
    }

    sessions.forEach(session => {
        const item = document.createElement("div");
        item.className = "session-item";
        item.dataset.id = session[0];
        item.dataset.pinned = session[3] || 0;
        item.dataset.archived = session[4] || 0;
        if (session[0] === currentSessionId) {
            item.classList.add("active");
        }

        const name = document.createElement("span");
        name.className = "session-name";
        name.innerText = getSessionDisplayName(session);
        name.title = name.innerText;
        name.onclick = () => loadSession(session[0]);

        const pinBadge = document.createElement("span");
        pinBadge.className = "pin-badge";
        pinBadge.innerText = "📌";
        pinBadge.title = "Pinned";
        if (String(session[3]) === "1" || session[3] === 1) {
            item.appendChild(pinBadge);
        }

        const menuButton = document.createElement("button");
        menuButton.className = "session-menu-btn";
        menuButton.innerText = "⋯";
        menuButton.onclick = (event) => showSessionMenu(event, session[0]);

        item.appendChild(name);
        item.appendChild(menuButton);
        sidebar.appendChild(item);
    });
}

/* ---------- Load one session ---------- */

function loadSession(sessionId) {
    currentSessionId = sessionId;

    fetch("/session/" + sessionId)
        .then(response => response.json())
        .then(chats => {
            const chatBox = document.getElementById("chatbox");
            chatBox.innerHTML = "";
            const chatTitle = document.getElementById("chatTitle");

            chats.forEach((chat, index) => {
                let user = chat[0];
                if (isJson(user)) {
                    try {
                        const arr = JSON.parse(user);
                        if (Array.isArray(arr) && arr.length && arr[0].content) {
                            user = arr[0].content;
                        }
                    } catch (e) { /* keep raw */ }
                }

                if (index === 0 && chatTitle && user) {
                    const t = String(user);
                    chatTitle.innerText = t.length > 40 ? t.slice(0, 40) + "…" : t;
                }

                chatBox.appendChild(buildUserRow(user));
                chatBox.appendChild(buildBotRow(chat[1]));
            });

            scrollToBottom();
            loadSessions();
        })
        .catch(err => console.error("loadSession error:", err));
}

/* ---------- New chat ---------- */

function startNewChat() {
    currentSessionId = crypto.randomUUID();

    const chatBox = document.getElementById("chatbox");
    if (chatBox) chatBox.innerHTML = "";

    const chartTitle = document.getElementById("chatTitle");
    if (chartTitle) chartTitle.innerText = "New chat";

    const input = document.getElementById("message");
    if (input) {
        input.value = "";
        input.disabled = false;
        input.focus();
    }

    const sendBtn = document.getElementById("sendBtn");
    if (sendBtn) sendBtn.disabled = false;

    loadSessions();
    closeSidebar();
}

/* ---------- Clear all chats ---------- */

function clearChat() {
    fetch("/clear-chat", { method: "DELETE" })
        .then(response => {
            if (!response.ok) throw new Error("HTTP Error: " + response.status);
            return response.json();
        })
        .then(() => {
            const chatBox = document.getElementById("chatbox");
            if (chatBox) chatBox.innerHTML = "";
            const chartTitle = document.getElementById("chatTitle");
            if (chartTitle) chartTitle.innerText = "New chat";
            loadSessions();
        })
        .catch(error => console.error("clearChat error:", error));
}

/* ---------- Single-session delete (kept for compatibility) ---------- */

async function deleteSession(sessionId) {
    const response = await fetch("/delete_session/" + sessionId, {
        method: "DELETE"
    });
    const data = await response.json();
    if (data.success) {
        if (currentSessionId === sessionId) {
            startNewChat();
        } else {
            loadSessions();
        }
    }
}

/* ---------- Session context menu ---------- */

function showSessionMenu(event, sessionId) {
    event.stopPropagation();
    selectedSessionId = sessionId;

    const item = document.querySelector(
        '#sessions .session-item[data-id="' + sessionId + '"]'
    );
    const isPinned = item && String(item.dataset.pinned) === "1";
    const isArchived = item && String(item.dataset.archived) === "1";

    const pinBtn = document.getElementById("menuPinBtn");
    const archiveBtn = document.getElementById("menuArchiveBtn");
    if (pinBtn) pinBtn.innerText = isPinned ? "📌 Unpin" : "📌 Pin";
    if (archiveBtn) {
        archiveBtn.innerText = (archivedView || isArchived)
            ? "📤 Unarchive"
            : "🗄 Archive";
    }

    const menu = document.getElementById("sessionMenu");
    menu.style.display = "block";
    menu.style.left = event.clientX + "px";
    menu.style.top = event.clientY + "px";
}

// Close the context menu when clicking anywhere else.
document.addEventListener("click", function () {
    const menu = document.getElementById("sessionMenu");
    if (menu) menu.style.display = "none";
});

/* ---------- Rename session (inline) ---------- */

async function renameSelectedSession() {
    if (!selectedSessionId) return;
    document.getElementById("sessionMenu").style.display = "none";

    const item = document.querySelector(
        '#sessions .session-item[data-id="' + selectedSessionId + '"]'
    );
    if (!item) return;

    const nameSpan = item.querySelector(".session-name");
    const currentText = nameSpan ? nameSpan.innerText : "Untitled";

    const input = document.createElement("input");
    input.className = "session-rename-input";
    input.value = currentText;

    nameSpan.replaceWith(input);
    renameInputEl = input;
    input.focus();
    input.select();

    const commitRename = async () => {
        if (renameInputEl !== input) return;
        renameInputEl = null;

        const newName = input.value.trim();
        if (newName && newName !== currentText) {
            try {
                await fetch("/rename_session/" + selectedSessionId, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name: newName })
                });
            } catch (e) {
                console.error("rename error:", e);
            }
        }
        loadSessions();
    };

    input.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            commitRename();
        } else if (e.key === "Escape") {
            renameInputEl = null;
            loadSessions();
        }
    });

    input.addEventListener("blur", commitRename);
}

/* ---------- Delete selected session ---------- */

async function deleteSelectedSession() {
    if (!selectedSessionId) return;

    if (!confirm("Delete this chat?")) return;

    const response = await fetch("/delete_session/" + selectedSessionId, {
        method: "DELETE"
    });
    const data = await response.json();

    document.getElementById("sessionMenu").style.display = "none";

    if (data.success) {
        if (currentSessionId === selectedSessionId) {
            startNewChat();
        } else {
            loadSessions();
        }
    } else {
        alert("Unable to delete chat.");
    }
}

/* ---------- Pin / Archive ---------- */

function toggleArchivedView() {
    archivedView = !archivedView;
    const btn = document.getElementById("archivedBtn");
    if (btn) {
        btn.classList.toggle("active", archivedView);
        btn.innerText = archivedView ? "💬 Chats" : "🗄 Archived";
    }
    if (archivedView) {
        loadArchivedSessions();
    } else {
        loadSessions();
    }
}

function refreshList() {
    if (archivedView) {
        loadArchivedSessions();
    } else {
        loadSessions();
    }
}

async function pinSelectedSession() {
    if (!selectedSessionId) return;

    const item = document.querySelector(
        '#sessions .session-item[data-id="' + selectedSessionId + '"]'
    );
    const isPinned = item && String(item.dataset.pinned) === "1";

    document.getElementById("sessionMenu").style.display = "none";

    const url = isPinned
        ? "/unpin_chat/" + selectedSessionId
        : "/pin_chat/" + selectedSessionId;

    try {
        await fetch(url, { method: "POST" });
    } catch (e) {
        console.error("pin toggle error:", e);
    }

    refreshList();
}

async function archiveSelectedSession() {
    if (!selectedSessionId) return;

    const item = document.querySelector(
        '#sessions .session-item[data-id="' + selectedSessionId + '"]'
    );
    const isArchived = item && String(item.dataset.archived) === "1";

    document.getElementById("sessionMenu").style.display = "none";

    const url = (archivedView || isArchived)
        ? "/unarchive_chat/" + selectedSessionId
        : "/archive_chat/" + selectedSessionId;

    try {
        await fetch(url, { method: "POST" });
    } catch (e) {
        console.error("archive toggle error:", e);
    }

    refreshList();
}

/* ---------- Responsive sidebar ---------- */

function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    if (sidebar) sidebar.classList.toggle("open");
}

function closeSidebar() {
    const sidebar = document.getElementById("sidebar");
    if (sidebar) sidebar.classList.remove("open");
}

/* ---------- Init ---------- */

window.onload = function () {
    loadSessions();
};