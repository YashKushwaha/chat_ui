// --- TEXTAREA HANDLING ---
export function sendMessage(textarea) {
    const message = textarea.value.trim();
    console.log('User message:', message);
    if (!message) return;

    const chatHistory = document.getElementById('chat-history');

    // Add user message
    const userMsgDiv = document.createElement('div');
    userMsgDiv.className = 'chat-message user-message';
    userMsgDiv.innerHTML = message.replace(/\n/g, '<br>');
    chatHistory.appendChild(userMsgDiv);

    // Clear input and reset textarea height
    textarea.value = '';
    textarea.style.height = 'auto';
    chatHistory.scrollTop = chatHistory.scrollHeight;

    // Send to backend
    fetch(window.CHAT_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
    })
    .then(response => response.json())
    .then(data => {
        // Log the server response to the console
        console.log('Server response:', data);

        const botMsgDiv = document.createElement('div');
        botMsgDiv.className = 'chat-message bot-message';

        // Ensure markdown is parsed correctly and render code blocks with custom styling
        //botMsgDiv.innerHTML = marked.parse((data.response || "No response").replace(/\n/g, '  \n'));
        botMsgDiv.innerHTML = marked.parse((data.response || "No response"));

        // Apply a custom class for code blocks
        const codeBlocks = botMsgDiv.querySelectorAll('pre code');
        codeBlocks.forEach(codeBlock => {
            codeBlock.parentElement.classList.add('highlighted-code');
        });

        chatHistory.appendChild(botMsgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

export function handleTextareaInput(textarea) {
    // Adjust the height of the textarea as the user types
    textarea.addEventListener('input', () => {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    });

    // Handle "Enter" key to send message without newline
    textarea.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();  // Prevent newline
            sendMessage(textarea);  // Call sendMessage when Enter is pressed
        }
    });
}
