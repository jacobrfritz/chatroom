import { z } from 'https://cdn.jsdelivr.net/npm/zod@3.22.4/+esm';


const MessageSchema = z.object({
  type: z.string().min(1, "Type is required"),
  message: z.string().min(1, "Username is required")
});

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

const loginOverlay = document.getElementById("login-overlay");
const usernameInput = document.getElementById("username-input");
const loginButton = document.getElementById("login-button");

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

function handleLogin() {
    const username = usernameInput.value.trim();
    if (!username) return;

    const identity = {
        type: "SET_IDENTITY",
        message: username
    };
    
    const result = MessageSchema.safeParse(identity);
    if (result.success) {
        websocket.send(JSON.stringify(identity));
        appendMessage(`${username} just connected!`, true);
        loginOverlay.style.display = "none";
    } else {
        alert(result.error.errors[0].message);
    }
}

loginButton.addEventListener("click", handleLogin);
usernameInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleLogin();
});

// Define the logic for when the connection starts
function initializeChat() {
    console.log("WebSocket connected");
}

// Handle the connection event
websocket.addEventListener("open", initializeChat);

// Handle incoming messages
websocket.addEventListener("message", (e) => {
    const message = JSON.parse(e.data);
    if(message.type === "MESSAGE"){
        console.log('valid incoming message');
        console.log(message.value);
        appendMessage(message.value);
    }
});

// Helper function to send messages
function sendMessage() {
    const message = input.value.trim();
    const out = {
        type: "MESSAGE",
        message: message
    };
    const result = MessageSchema.safeParse(out)
    if(result.success){
        if(websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify(out));
        input.value = "";
    }
    }
    
}

send_button.addEventListener("click", sendMessage);

input.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});