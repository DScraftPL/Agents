
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
            displayRecipes();
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
    .then(response => {
        displayThrobber(false);
        if (response.ok) {
            return response.json();
        } else {
            return response.json().then(error => {throw new Error(error.error)});
        }
    })
    .then(data => {
        chatBox.innerHTML += `<div>Agent: ${data.message}</div>`;
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);
    });
}

function displayRecipes() {
    const token = localStorage.getItem('token');

    fetch('http://127.0.0.1:5000/recipes', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            return response.json().then(error => {throw new Error(error.error)});
        }
    })
    .then(data => {
        const recipes = data.recipes;
        const recipeSidebar = document.getElementById('recipe-sidebar');
        recipeSidebar.innerHTML = '<h3>My Recipes</h3>';
        recipes.forEach(recipe => {
            recipeSidebar.innerHTML += `<div><strong>${recipe[1]}</strong><p>${recipe[2]}</p></div>`;
        });
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);
    });
}
