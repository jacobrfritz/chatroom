const send_button = document.getElementById("send_button");
const chatbox = document.getElementById('chatbox');
const input = document.getElementById("chat");
const themeToggle = document.getElementById("theme-toggle");

// --- Theme Management ---
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}

// Initialize theme
const savedTheme = localStorage.getItem('theme');
const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
if (savedTheme) {
    setTheme(savedTheme);
} else if (systemDark) {
    setTheme('dark');
}

themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    setTheme(currentTheme === 'dark' ? 'light' : 'dark');
});

// --- Chat Logic ---
const url = `ws://${window.location.hostname}:8765`;
const websocket = new WebSocket(url);

function appendMessage(text, isSystem = false) {
    const p = document.createElement("p");
    if (isSystem) p.classList.add('system-message');
    p.textContent = text;
    chatbox.append(p);
    chatbox.scrollTop = chatbox.scrollHeight;
}

// Define the logic for when the connection starts
function initializeChat() {
    let username = null;
    while(!username){
        username = prompt("Enter a Username:");
    }
    appendMessage("Connected!", true);
    const identity = {
        type: "SET_IDENTITY",
        username: username
    };
    websocket.send(JSON.stringify(identity));
}

// Handle the connection event
websocket.addEventListener("open", initializeChat);

// Handle incoming messages
websocket.addEventListener("message", (e) => {
    appendMessage(e.data);
});

// Helper function to send messages
function sendMessage() {
    const message = input.value.trim();
    const out = {
        type: "MESSAGE",
        message: message
    };
    if (message && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify(out));
        input.value = "";
    }
}

send_button.addEventListener("click", sendMessage);

// Fixed: Added 'event' parameter to the listener
input.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});