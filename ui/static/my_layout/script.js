document.querySelectorAll('.toggle-btn').forEach(button => {
  button.addEventListener('click', () => {
    button.classList.toggle('active');
  });
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
