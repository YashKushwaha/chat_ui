// --- TEXTAREA HANDLING ---
export function sendMessage(textarea) {
    const message = textarea.value.trim();
    console.log(message);
    if (!message) return;
  
    const chatHistory = document.getElementById('chat-history');
  
    // Add user message
    const userMsgDiv = document.createElement('div');
    userMsgDiv.className = 'chat-message user-message';
    userMsgDiv.innerHTML = message.replace(/\n/g, '<br>');
    chatHistory.appendChild(userMsgDiv);
  
    // Clear input
    textarea.value = '';
    textarea.style.height = 'auto';
    chatHistory.scrollTop = chatHistory.scrollHeight;
  
    // Send to backend
    fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    })
    .then(response => response.json())
    .then(data => {
      console.log('Server response:', data);
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
  
  export function handleTextareaInput(textarea) {
    textarea.addEventListener('input', () => {
      textarea.style.height = 'auto';
      textarea.style.height = textarea.scrollHeight + 'px';
    });
  
    textarea.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();  // Stop newline
        sendMessage(textarea);
      }
    });
  }
  