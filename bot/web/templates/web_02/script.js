let token = null;
let chatId = 1;

// --- Setup Listeners ---
function setupChatListeners() {
    const messageInput = document.getElementById("message");
    messageInput.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            event.preventDefault(); 
            sendMessage();
        }
    });
    messageInput.focus();
}

function setupAuthListeners() {
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");

    usernameInput.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            event.preventDefault(); 
            passwordInput.focus();
        }
    });

    passwordInput.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            event.preventDefault(); 
            login(); 
        }
    });
    
    // Auto focus username on load
    usernameInput.focus();
}

// --- API Functions ---
function register() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    fetch("/register", {
        method: "POST",
        body: new URLSearchParams({ username, password })
    })
    .then(res => res.json())
    .then(data => alert("SYSTEM MSG: " + (data.msg || JSON.stringify(data))));
}

function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    fetch("/login", {
        method: "POST",
        body: new URLSearchParams({ username, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.access_token) {
            token = data.access_token;
            document.getElementById("auth").style.display = "none";
            document.getElementById("chat").style.display = "flex"; // Flex for terminal layout
            setupChatListeners();
        } else {
            alert("ACCESS DENIED: Invalid Credentials");
        }
    });
}

function sendMessage() {
    const messageInput = document.getElementById("message");
    const message = messageInput.value;
    
    if (!message.trim()) {
        messageInput.focus();
        return; 
    }
    
    messageInput.value = "";
    messageInput.focus();

    // Optimistic UI: Show user message immediately
    const historyDiv = document.getElementById("history");
    // We wait for server response to render full history to keep it synced
    
    // Add temporary loading indicator
    const loadingDiv = document.createElement("div");
    loadingDiv.className = "sys-msg";
    loadingDiv.textContent = "TRANSMITTING DATA...";
    historyDiv.appendChild(loadingDiv);
    historyDiv.scrollTop = historyDiv.scrollHeight;

    fetch(`/chat/${chatId}`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message })
    })
    .then(res => res.json())
    .then(data => {
        historyDiv.innerHTML = ""; // Clear for fresh render from server state
        
        // Add initial system boot messages
        const boot1 = document.createElement("div"); boot1.className="sys-msg"; boot1.textContent="CONNECTION ESTABLISHED...";
        historyDiv.appendChild(boot1);
        
        data.history.forEach(entry => {
            const div = document.createElement("div");
            div.className = entry.role === "user" ? "message-user" : "message-assistant";
            div.textContent = entry.content; // CSS ::before handles the prefixes
            historyDiv.appendChild(div);
        });
        historyDiv.scrollTop = historyDiv.scrollHeight; 
    })
    .catch(error => {
        console.error("Error:", error);
        alert("CRITICAL ERROR: Connection Lost");
    });
}

document.addEventListener('DOMContentLoaded', setupAuthListeners);