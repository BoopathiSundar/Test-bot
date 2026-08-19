async function sendMessage() {

    let message = document.getElementById("message").value;

    let chatBox = document.getElementById("chatbox");
    
    chatBox.innerHTML +=
        "<div class='user'>" + message + "</div>";

    document.getElementById("message").value = "";

    // Create an empty bot message
    let botDiv = document.createElement("div");

    botDiv.className = "bot";

    botDiv.innerHTML = "";

    chatBox.appendChild(botDiv);

    const response = await fetch("/chat-stream", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            messages: [
                {
                    role: "user",
                    content: message
                }
            ]
        })

    });

    const reader = response.body.getReader();

    const decoder = new TextDecoder();

    let fullResponse = "";

    while (true) {

        const { value, done } = await reader.read();

        if (done)
            break;

        const chunk = decoder.decode(value);

        botDiv.innerHTML += chunk;

        //botDiv.innerHTML = marked.parse(fullResponse);

        chatBox.scrollTop = chatBox.scrollHeight;
    }

}

function loadSessions() {
    fetch("/sessions")
        .then(response => response.json())
        .then(sessions => {
            //console.log(sessions)
            const sidebar = document.getElementById("sessions");
            console.log(typeof(sidebar))
            sidebar.innerHTML = "";

            sessions.forEach(session => {

                const item = document.createElement("div");
                item.className = "session-item";

                const name = document.createElement("span");

                name.className = "session-name";
                name.innerText = session[1];

                if (isJson(session[1])) {

                    const jsonData = JSON.parse(session[1]);

                    if (jsonData.length > 0 && jsonData[0].content) {
                        name.innerText = jsonData[0].content;
                    }
                }

                const menuButton = document.createElement("button");

                menuButton.className = "session-menu-btn";
                menuButton.innerText = "⋯";

                name.onclick = () => {
                    loadSession(session[0]);
                };

                menuButton.onclick = (event) => {
                    showSessionMenu(event, session[0]);
                };

                item.appendChild(name);
                item.appendChild(menuButton);

                sidebar.appendChild(item);
            });
        });
}

function isJson(value) {
    try {
        JSON.parse(value);
        return true;
    } catch (e) {
        return false;
    }
}

function loadSession(sessionId) {

    fetch("/session/" + sessionId)
        .then(response => response.json())
        .then(chats => {

            const chatBox = document.getElementById("chatbox"); // Your chat container
            chatBox.innerHTML = "";
            userArrMessage = ""
            chats.forEach(chat => {
                
                if (isJson(chat[0])) {
                    chatBox.innerHTML += `
                    <div class="user-message">
                        ${JSON.parse(chat[0])[0].content}
                    </div>
                `;
                } else {
                // User message
                chatBox.innerHTML += `
                    <div class="user-message">
                        ${chat[0]}
                    </div>
                `;
                }

                // Bot response
                chatBox.innerHTML += `
                    <div class="bot-message">
                        ${chat[1]}
                    </div>
                `;
            });

            // Scroll to the bottom
            chatBox.scrollTop = chatBox.scrollHeight;
        });
}

function startNewChat() {

    currentSessionId = crypto.randomUUID();

    // Clear the chat window
    document.getElementById("chatbox").innerHTML = "";

    // Clear the input
    document.getElementById("message").value = "";

    // Optional: reload the sidebar
    loadSessions();
}

function clearChat(){
    fetch("/clear-chat",  {

        method: "DELETE"
        })
        .then(response => {
        if (!response.ok) {
            throw new Error("HTTP Error: " + response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log("Response:", data);
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

async function deleteSession(sessionId) {

    const response = await fetch(
        "/delete_session/" + sessionId,
        {
            method: "DELETE"
        }
    );

    const data = await response.json();

    if (data.success) {
        location.reload();
    }
}

let selectedSessionId = null;

function showSessionMenu(event, sessionId) {

    event.stopPropagation();

    selectedSessionId = sessionId;

    const menu = document.getElementById("sessionMenu");

    menu.style.display = "block";

    menu.style.left = event.clientX + "px";
    menu.style.top = event.clientY + "px";
}

document.addEventListener("click", function () {

    document.getElementById("sessionMenu").style.display = "none";

});

async function deleteSelectedSession() {

    if (!selectedSessionId) {
        return;
    }

    const confirmed = confirm("Delete this chat?");

    if (!confirmed) {
        return;
    }

    const response = await fetch(
        `/delete_session/${selectedSessionId}`,
        {
            method: "DELETE"
        }
    );

    const data = await response.json();

    if (data.success) {

        document.getElementById("sessionMenu").style.display = "none";

        // Reload session list
        location.reload();

    } else {

        alert("Unable to delete chat.");

    }

}

window.onload = function () {
    loadSessions();
};