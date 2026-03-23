document.getElementById('send-button').addEventListener('click', function() {
    const message = document.getElementById('message-input').value;
    if (message.trim() === '') { return; }
    appendMessage(`You: ${message}`);
    document.getElementById('message-input').value = '';

    fetch('http://localhost:5000/api/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message })
    }).then(response => response.json())
      .then(data => {
          if (data.error) {
              console.error('Error:', data.error);
          } else {
              appendMessage(`AI: ${data.response}`);
          }
      }).catch(error => {
          console.error('Error:', error);
      });
});

function appendMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.textContent = message;
    document.getElementById('messages').appendChild(messageElement);
    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
}