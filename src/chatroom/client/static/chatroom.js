const send_button = document.getElementById("send_button");
const chatbox = document.getElementById('chatbox');
const input = document.getElementById("chat");

const url = `ws://${window.location.hostname}:8765`;
const websocket = new WebSocket(url);

// Define the logic for when the connection starts
function initializeChat() {
    let username = null;
    while(!username){
        username = prompt("Enter a Username:");
    }
    chatbox.append("Connected!");
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
    const p = document.createElement("p");
    p.textContent = e.data;
    chatbox.append(p);
    chatbox.scrollTop = chatbox.scrollHeight;
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