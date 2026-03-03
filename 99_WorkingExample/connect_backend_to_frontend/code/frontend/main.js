document.addEventListener('DOMContentLoaded', () => {
    const sendButton = document.getElementById('send-button');
    const userInput = document.getElementById('user-input');
    const messages = document.getElementById('messages');

    sendButton.addEventListener('click', () => {
        const userQuery = userInput.value;
        if (userQuery.trim() !== '') {
            displayMessage('User: ' + userQuery);
            getAIResponse(userQuery);
            userInput.value = '';
        }
    });

    function displayMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.textContent = message;
        messages.appendChild(messageElement);
        messages.scrollTop = messages.scrollHeight;
    }

    function getAIResponse(query) {
        fetch('http://127.0.0.1:5000/ai', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query }),
        })
        .then(response => response.json())
        .then(data => {
            displayMessage(data.response);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});
