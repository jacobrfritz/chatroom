import { z } from 'https://cdn.jsdelivr.net/npm/zod@3.22.4/+esm';
import { Filter } from 'https://esm.sh/bad-words@4.0.0';

const filter = new Filter();

const MessageSchema = z.object({
  type: z.string().min(1, "Type is required"),
  message: z.string().min(1, "Username is required")
});

const IdentitySchema = z.object({
  username: z.string().min(3).max(20).trim(),
  uuid: z.string().uuid({ message: "Invalid UUID format" })
});

const identity = null;

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
const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
// Fallback for local development: if on port 8080, connect directly to 8765.
// In production (proxied), use the /chat-ws/ path.
const wsUrl = window.location.port === '8080' 
    ? `${wsProtocol}${window.location.hostname}:8765` 
    : `${wsProtocol}${window.location.host}/chat-ws/`;
const websocket = new WebSocket(wsUrl);

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

    if (filter.isProfane(username)) {
        alert("Username contains profanity. Please pick another one.");
        return;
    }

    const identity = {
        type: "SET_IDENTITY",
        message: username
    };
    
    const result = MessageSchema.safeParse(identity);

    if (result.success) {
        if (websocket.readyState === WebSocket.OPEN) {
            websocket.send(JSON.stringify(identity));
            loginOverlay.style.display = "none";
        } else {
            alert("Connecting to server... Please try again in a moment.");
        }
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
    if(message.message_type === "MESSAGE"){
        console.log('valid incoming message');
        console.log(message);
        appendMessage(message.value);
    } else if (message.message_type === "CONNECTED") {
        appendMessage(message.value, true);
    }
});

// Helper function to send messages
function sendMessage() {
    const message = input.value.trim();
    const cleanMessage = filter.clean(message);
    const out = {
        type: "MESSAGE",
        message: cleanMessage
    };
    const result = MessageSchema.safeParse(out);
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