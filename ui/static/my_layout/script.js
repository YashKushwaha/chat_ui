console.log("Script loaded");

// --- TOGGLE BUTTON HANDLING ---
const toggleStates = {};
document.querySelectorAll('.toggle-btn').forEach(button => {
  const option = button.dataset.option;
  toggleStates[option] = false; // default state

  button.addEventListener('click', () => {
    toggleStates[option] = !toggleStates[option];
    button.classList.toggle('active', toggleStates[option]);
    console.log(`Toggled ${option}: ${toggleStates[option]}`);
  });
});

// --- TEXTAREA HANDLING ---
const textarea = document.getElementById('userInput');

function sendMessage() {
  const message = textarea.value.trim();
  if (!message) return;

  const chatHistory = document.getElementById('chat-history');

  // Add user message
  const userMsgDiv = document.createElement('div');
  userMsgDiv.className = 'chat-message user-message';
  userMsgDiv.textContent = message;
  chatHistory.appendChild(userMsgDiv);

  // Clear input
  textarea.value = '';
  textarea.style.height = 'auto';
  chatHistory.scrollTop = chatHistory.scrollHeight;

  // Send to backend
  fetch('/test', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  })
  .then(response => response.json())
  .then(data => {
    const botMsgDiv = document.createElement('div');
    botMsgDiv.className = 'chat-message bot-message';
    botMsgDiv.innerHTML = marked.parse((data.response || "No response").replace(/\n/g, '  \n'));
    chatHistory.appendChild(botMsgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

// Handle Enter / Shift+Enter
textarea.addEventListener('keydown', function (e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();  // Stop newline
    sendMessage();
  }
});

// Auto-resize as user types
textarea.addEventListener('input', () => {
  textarea.style.height = 'auto';
  textarea.style.height = textarea.scrollHeight + 'px';
});

// --- FILE UPLOAD HANDLING ---
document.getElementById("file-upload").addEventListener("change", async function () {
  const file = this.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();
    alert(result.message); // or update the UI
  } catch (error) {
    console.error("Upload failed:", error);
    alert("Upload failed. Please try again.");
  }

  this.value = ""; // reset file input
});
