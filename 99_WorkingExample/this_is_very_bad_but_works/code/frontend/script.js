document.getElementById('register-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    fetch('http://localhost:5000/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
    });
});





document.getElementById('login-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.access_token) {
            localStorage.setItem('token', data.access_token);
            document.getElementById('auth').style.display = 'none';
            document.getElementById('dashboard').style.display = 'block';
        } else {
            alert(data.message);
        }
    });
});



document.getElementById('agent-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const aiResponse = document.getElementById('agent-input').value;

    fetch('http://localhost:5000/agent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ ai_response: aiResponse })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
    });
});

document.getElementById('fetch-recipes').addEventListener('click', function() {
    fetch('http://localhost:5000/recipes', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
    })
    .then(res => res.json())
    .then(data => {
        const recipesDiv = document.getElementById('recipes');
        recipesDiv.innerHTML = '';
        if (Array.isArray(data)) {
            data.forEach(recipe => {
                const recipeDiv = document.createElement('div');
                recipeDiv.textContent = typeof recipe === 'object' ? JSON.stringify(recipe) : recipe;
                recipesDiv.appendChild(recipeDiv);
            });
        } else {
            recipesDiv.textContent = JSON.stringify(data);
        }
    })
    .catch(err => {
        alert('Error fetching recipes: ' + err.message);
    });
});
