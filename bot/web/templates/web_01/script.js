let token = null;
let chatId = 1; // simple default chat session

// --- Utility function to set up listeners for the chat input ---
function setupChatListeners() {
    const messageInput = document.getElementById("message");
    
    // Listener for sending the message on Enter key press
    messageInput.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            event.preventDefault(); 
            sendMessage();
        }
    });
    
    // After setup, focus on the input for immediate typing
    messageInput.focus();
}

// --- Utility function to set up listeners for login inputs ---
function setupAuthListeners() {
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");

    // Listener for Login on Enter key press in username field
    usernameInput.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            event.preventDefault(); 
            // Move focus to password
            passwordInput.focus();
        }
    });

    // Listener for Login on Enter key press in password field
    passwordInput.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            event.preventDefault(); 
            login(); // Attempt login
        }
    });
}


function register() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    fetch("/register", {
        method: "POST",
        body: new URLSearchParams({ username, password })
    })
    .then(res => res.json())
    .then(data => alert(data.msg || JSON.stringify(data)));
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
            document.getElementById("chat").style.display = "flex"; // Note: Set to 'flex' as per new CSS
            
            // --- Crucial: Call the chat setup function after successful login ---
            setupChatListeners();
            
        } else {
            alert("Login failed");
        }
    });
}

function sendMessage() {
    const message = document.getElementById("message").value;
    
    // Do not send empty messages
    if (!message.trim()) {
        document.getElementById("message").focus();
        return; 
    }
    
    document.getElementById("message").value = "";
    document.getElementById("message").focus(); // Keep focus for quick follow-up

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
        const historyDiv = document.getElementById("history");
        // Clear history and append messages
        historyDiv.innerHTML = ""; 
        data.history.forEach(entry => {
            const div = document.createElement("div");
            div.className = entry.role === "user" ? "message-user" : "message-assistant";
            // Check if content exists before trying to access it
            div.textContent = entry.content ? entry.content : `[Empty response]`; 
            historyDiv.appendChild(div);
        });
        // Scroll to the bottom
        historyDiv.scrollTop = historyDiv.scrollHeight; 
    })
    .catch(error => {
        console.error("Error sending message:", error);
        alert("Failed to send message or receive a response.");
    });
}

// --- Initial Setup: Run this when the script loads to set up auth listeners ---
// This ensures that hitting Enter in the login fields works right away.
document.addEventListener('DOMContentLoaded', setupAuthListeners);