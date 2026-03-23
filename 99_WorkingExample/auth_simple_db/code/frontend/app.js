
function register() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('http://localhost:5000/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
        .then(response => response.json())
        .then(data => alert(data.message));
}

function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Login successful!') {
                alert(data.message);
                fetchRecipes();
            } else {
                alert(data.message);
            }
        });
}

function fetchRecipes() {
    fetch('http://localhost:5000/recipes')
        .then(response => response.json())
        .then(data => {
            const recipeList = document.getElementById('recipeList');
            recipeList.innerHTML = '';
            data.forEach(recipe => {
                const li = document.createElement('li');
                li.textContent = recipe.title;
                recipeList.appendChild(li);
            });
        });
}

function sendMessage() {
    const chatInput = document.getElementById('chatInput').value;

    // Placeholder: Integrate this with actual AI interactions
    const generatedRecipe = {
        title: 'Mock Recipe',
        content: chatInput
    };

    fetch('http://localhost:5000/add_recipe', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(generatedRecipe)
    })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            fetchRecipes();
        });
}
