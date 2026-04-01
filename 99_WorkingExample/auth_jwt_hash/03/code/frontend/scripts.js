function register() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    fetch('http://127.0.0.1:5000/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => console.error('Error:', error));
}

function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
            localStorage.setItem('token', data.token); // Store the token in localStorage
            document.getElementById('user-container').style.display = 'none';
            document.getElementById('chat-container').style.display = 'block';
        } else {
            alert(data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

function displayThrobber(display) {
    const throbber = document.getElementById('throbber');
    if (display) {
        throbber.style.display = 'block';
    } else {
        throbber.style.display = 'none';
    }
}

function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    const chatBox = document.getElementById('chat-box');
    const token = localStorage.getItem('token');
    chatBox.innerHTML += `<div>User: ${userInput}</div>`;

    displayThrobber(true);

    fetch('http://127.0.0.1:5000/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        chatBox.innerHTML += `<div>Agent: ${data.message}</div>`;
        displayThrobber(false);
    })
    .catch(error => {
        console.error('Error:', error);
        displayThrobber(false);
    });
}
