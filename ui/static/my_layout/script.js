console.log("Script loaded");

document.querySelectorAll('.toggle-btn').forEach(button => {
  button.addEventListener('click', () => {
    button.classList.toggle('active');
  });
});

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
    alert(result.message); // or update the UI with a success message
  } catch (error) {
    console.error("Upload failed:", error);
    alert("Upload failed. Please try again.");
  }

  // Reset input so the same file can be selected again if needed
  this.value = "";
});


document.getElementById('message-form').addEventListener('submit', function (e) {
  e.preventDefault();

  const input = document.getElementById('message-input');
  const message = input.value.trim();
  if (message === '') return;

  const chatHistory = document.getElementById('chat-history');

  const userMsgDiv = document.createElement('div');
  userMsgDiv.className = 'chat-message user-message';
  userMsgDiv.textContent = message;
  chatHistory.appendChild(userMsgDiv);

  input.value = '';
  chatHistory.scrollTop = chatHistory.scrollHeight;

  // Log the message payload
  console.log(JSON.stringify({ message }));

  fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  })
  .then(response => response.json())
  .then(data => {
    const botMsgDiv = document.createElement('div');
    botMsgDiv.className = 'chat-message bot-message';
    botMsgDiv.textContent = data.response || "No response";
    chatHistory.appendChild(botMsgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
  })
  .catch(error => {
    console.error('Error:', error);
  });
});

const toggleStates = {};

document.querySelectorAll('.toggle-btn').forEach(button => {
  const option = button.dataset.option;
  toggleStates[option] = false; // default state

  button.addEventListener('click', () => {
    // Toggle state
    toggleStates[option] = !toggleStates[option];

    // Update button appearance
    button.classList.toggle('active', toggleStates[option]);

    // Log the updated state (or send it to server)
    console.log(`Toggled ${option}: ${toggleStates[option]}`);
  });
});
